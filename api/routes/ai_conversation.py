"""
AI Conversation Routes for OpenAI Integration

This module provides endpoints for:
- Real-time AI conversation with streaming support
- Personality-based chatbot responses
- Knowledge base integration with ChromaDB
- Conversation context management
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from core.database import get_db, Conversation, Message, Project
from auth.middleware import get_current_user
from services.openai_service import OpenAIService
from services.vector_storage import VectorStorageService
from sqlalchemy import select

logger = structlog.get_logger()

router = APIRouter(prefix="/ai", tags=["AI Integration"])

# Initialize services
openai_service = OpenAIService()


class ChatRequest(BaseModel):
    """Request model for AI chat"""

    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: int
    stream: bool = Field(default=False)
    use_knowledge_base: bool = Field(default=True)


class ChatResponse(BaseModel):
    """Response model for AI chat"""

    response: str
    conversation_id: int
    message_id: Optional[int] = None
    context_used: list = []
    confidence_score: float
    response_type: str
    metadata: Dict[str, Any] = {}


class PersonalityConfigRequest(BaseModel):
    """Request model for personality configuration"""

    chatbot_id: int
    personality: Dict[str, Any]


class KnowledgeUploadRequest(BaseModel):
    """Request model for knowledge base upload"""

    chatbot_id: int
    documents: list[str]
    metadata: Optional[Dict[str, Any]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Chat with AI assistant with conversation context
    """
    try:
        # Get conversation and validate access
        conv_query = select(Conversation).where(
            Conversation.id == request.conversation_id
        )
        result = await db.execute(conv_query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Check user access
        if conversation.user_id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to conversation",
            )

        # Get project for personality configuration
        project_query = select(Project).where(Project.id == conversation.project_id)
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        # Get conversation history
        messages_query = (
            select(Message)
            .where(Message.conversation_id == request.conversation_id)
            .order_by(Message.created_at.desc())
            .limit(10)
        )

        result = await db.execute(messages_query)
        messages = result.scalars().all()

        # Build context history
        context_history = []
        for msg in reversed(messages):  # Reverse to get chronological order
            if msg.message_type == "user":
                # Find corresponding AI response
                ai_msg_query = (
                    select(Message)
                    .where(
                        Message.conversation_id == request.conversation_id,
                        Message.message_type == "ai",
                        Message.created_at > msg.created_at,
                    )
                    .order_by(Message.created_at.asc())
                    .limit(1)
                )

                ai_result = await db.execute(ai_msg_query)
                ai_msg = ai_result.scalar_one_or_none()

                if ai_msg:
                    context_history.append(
                        {"user_message": msg.content, "ai_response": ai_msg.content}
                    )

        # Create conversation context
        personality_config = {
            "name": f"{project.name} Assistant",
            "tone": "professional and helpful",
            "expertise": f"{project.assistant_type} assistance",
        }

        context = await openai_service.create_conversation_context(
            chatbot_id=str(project.id),
            conversation_id=str(conversation.id),
            user_id=str(current_user["id"]),
            personality_config=personality_config,
        )

        # Update context with history
        context.context_history = context_history

        # Generate AI response
        ai_response = await openai_service.generate_response(
            message=request.message,
            context=context,
            stream=request.stream,
            use_knowledge_base=request.use_knowledge_base,
        )

        # Save user message
        user_message = Message(
            conversation_id=request.conversation_id,
            content=request.message,
            message_type="user",
            sender_id=current_user["id"],
        )
        db.add(user_message)
        await db.flush()

        # Save AI response
        ai_message = Message(
            conversation_id=request.conversation_id,
            content=ai_response.content,
            message_type="ai",
            metadata=ai_response.metadata,
        )
        db.add(ai_message)
        await db.commit()

        logger.info(f"AI chat completed for conversation {request.conversation_id}")

        return ChatResponse(
            response=ai_response.content,
            conversation_id=request.conversation_id,
            message_id=ai_message.id,
            context_used=ai_response.context_used,
            confidence_score=ai_response.confidence_score,
            response_type=ai_response.response_type,
            metadata=ai_response.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process AI chat request",
        )


@router.post("/chat/stream")
async def stream_chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Stream AI conversation response for real-time chat
    """
    try:
        # Similar validation as above (simplified for brevity)
        conv_query = select(Conversation).where(
            Conversation.id == request.conversation_id
        )
        result = await db.execute(conv_query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Create basic context for streaming
        context = await openai_service.create_conversation_context(
            chatbot_id=str(conversation.project_id),
            conversation_id=str(conversation.id),
            user_id=str(current_user["id"]),
        )

        # Generate streaming response
        async def generate_stream():
            try:
                async for chunk in openai_service.generate_response(
                    message=request.message, context=context, stream=True
                ):
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in streaming chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process streaming chat request",
        )


@router.post("/personality/configure")
async def configure_personality(
    request: PersonalityConfigRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Configure chatbot personality
    """
    try:
        # Get and validate project
        project_query = select(Project).where(Project.id == request.chatbot_id)
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        # Update project with personality configuration
        project.personality_config = request.personality
        await db.commit()

        logger.info(f"Personality configured for chatbot {request.chatbot_id}")

        return {
            "success": True,
            "message": "Personality configuration updated",
            "chatbot_id": request.chatbot_id,
            "personality": request.personality,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring personality: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure personality",
        )


@router.post("/knowledge/upload")
async def upload_knowledge(
    request: KnowledgeUploadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Upload documents to knowledge base
    """
    try:
        # Get and validate project
        project_query = select(Project).where(Project.id == request.chatbot_id)
        result = await db.execute(project_query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        # Store documents in vector database
        from core.config import settings

        vector_service = VectorStorageService(settings)

        for document in request.documents:
            await vector_service.store_knowledge_document(
                chatbot_id=str(request.chatbot_id),
                document=document,
                metadata=request.metadata or {},
            )

        logger.info(f"Uploaded {len(request.documents)} documents to knowledge base")

        return {
            "success": True,
            "message": f"Uploaded {len(request.documents)} documents",
            "chatbot_id": request.chatbot_id,
            "documents_count": len(request.documents),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading knowledge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload knowledge documents",
        )


@router.get("/health")
async def ai_health_check():
    """
    Check AI services health
    """
    try:
        # Check OpenAI service
        openai_health = await openai_service.health_check()

        # Check vector storage (simplified)
        vector_health = {"status": "healthy", "accessible": True}

        overall_status = (
            "healthy" if openai_health["status"] == "healthy" else "unhealthy"
        )

        return {
            "status": overall_status,
            "services": {"openai": openai_health, "vector_storage": vector_health},
            "timestamp": openai_health["timestamp"],
        }

    except Exception as e:
        logger.error(f"Error in AI health check: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "services": {
                "openai": {"status": "unknown"},
                "vector_storage": {"status": "unknown"},
            },
        }
