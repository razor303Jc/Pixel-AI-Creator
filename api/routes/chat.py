"""
Chat API Routes

Simplified chat endpoints that match test expectations.
These provide easy-to-use chat functionality for frontend integration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
from datetime import datetime
import logging

# Import authentication
from auth.middleware import get_current_user

# Import database
from core.database import get_db, Conversation, Message

# Import models
from models.conversation import (
    MessageCreate,
    MessageResponse,
    ConversationResponse,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get conversations for the current user.
    Simple endpoint for frontend chat interface.
    """
    try:
        # Query conversations for the current user
        conversations_query = (
            select(Conversation)
            .where(Conversation.user_id == current_user["user_id"])
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        result = await db.execute(conversations_query)
        conversations = result.scalars().all()
        
        response_conversations = []
        for conv in conversations:
            # Get message count
            message_count_query = select(Message.id).where(
                Message.conversation_id == conv.id
            )
            message_count_result = await db.execute(message_count_query)
            message_count = len(message_count_result.scalars().all())
            
            # Get last message time
            last_message_query = (
                select(Message.created_at)
                .where(Message.conversation_id == conv.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            )
            last_message_result = await db.execute(last_message_query)
            last_message_at = last_message_result.scalar_one_or_none()
            
            response_conversations.append(
                ConversationResponse(
                    id=conv.id,
                    project_id=conv.project_id,
                    user_id=conv.user_id,
                    title=conv.title,
                    status=conv.status,
                    message_count=message_count,
                    metadata=conv.extra_data or {},
                    created_at=conv.created_at,
                    updated_at=conv.updated_at,
                    last_message_at=last_message_at,
                )
            )
        
        logger.info(
            f"Retrieved {len(response_conversations)} conversations "
            f"for user {current_user['email']}"
        )
        return response_conversations
        
    except Exception as e:
        logger.error(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations",
        )


@router.post("/send", response_model=MessageResponse)
async def send_chat_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Send a message to a conversation.
    Simple endpoint for frontend chat interface.
    """
    try:
        # Verify conversation exists and user has access
        conversation_query = select(Conversation).where(
            and_(
                Conversation.id == message_data.conversation_id,
                Conversation.user_id == current_user["user_id"],
            )
        )
        conversation_result = await db.execute(conversation_query)
        conversation = conversation_result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied",
            )
        
        # Create the message
        message = Message(
            conversation_id=message_data.conversation_id,
            content=message_data.content,
            message_type=message_data.message_type or "user",
            metadata=message_data.metadata or {},
            created_at=datetime.utcnow(),
        )
        
        db.add(message)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(message)
        
        response = MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            content=message.content,
            message_type=message.message_type,
            metadata=message.metadata or {},
            created_at=message.created_at,
        )
        
        logger.info(
            f"Message sent by user {current_user['email']} "
            f"to conversation {message_data.conversation_id}"
        )
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message",
        )


@router.post("/message", response_model=MessageResponse)
async def create_chat_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a message in a conversation.
    Alternative endpoint name for backward compatibility.
    """
    # This is the same as send_chat_message but with different route name
    # to match test expectations
    return await send_chat_message(message_data, db, current_user)


@router.get("/health")
async def chat_health():
    """
    Simple health check for chat service.
    """
    return {
        "status": "healthy",
        "service": "chat",
        "timestamp": datetime.utcnow().isoformat(),
    }
