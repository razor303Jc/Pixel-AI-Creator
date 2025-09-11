"""
OpenAI Service for AI Integration Implementation
"""

import json
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime
from dataclasses import dataclass

from openai import AsyncOpenAI
import structlog

from core.config import settings
from services.vector_storage import VectorStorageService

logger = structlog.get_logger()


@dataclass
class ConversationContext:
    """Context for maintaining conversation state"""

    chatbot_id: str
    conversation_id: str
    user_id: str
    personality: Dict[str, Any]
    context_history: List[Dict[str, str]]
    knowledge_base: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """Structured AI response with metadata"""

    content: str
    context_used: List[str]
    confidence_score: float
    response_type: str
    metadata: Dict[str, Any]


class OpenAIService:
    """Enhanced OpenAI service for AI integration"""

    def __init__(self):
        """Initialize OpenAI service with configuration"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-4"
        self.streaming_model = "gpt-4"

        # Context management
        self.max_context_messages = 10
        self.context_window_tokens = 4000

        logger.info("OpenAI service initialized successfully")

    async def generate_response(
        self,
        message: str,
        context: ConversationContext,
        stream: bool = False,
        use_knowledge_base: bool = True,
    ) -> Union[AIResponse, AsyncGenerator[str, None]]:
        """Generate AI response with context awareness"""
        try:
            # Build conversation messages
            messages = await self._build_conversation_messages(message, context)

            # Generate response
            if stream:
                return self._stream_response(messages, context)
            else:
                return await self._generate_complete_response(messages, context)

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise

    async def _build_conversation_messages(
        self, message: str, context: ConversationContext
    ) -> List[Dict[str, str]]:
        """Build conversation messages for OpenAI API"""
        messages = []

        # System message with personality
        system_prompt = self._build_system_prompt(context)
        messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        recent_history = context.context_history[-self.max_context_messages :]
        for msg in recent_history:
            messages.extend(
                [
                    {"role": "user", "content": msg.get("user_message", "")},
                    {"role": "assistant", "content": msg.get("ai_response", "")},
                ]
            )

        # Add current message
        messages.append({"role": "user", "content": message})

        return messages

    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build system prompt with personality configuration"""
        personality = context.personality

        assistant_name = personality.get("name", "an AI assistant")
        tone = personality.get("tone", "professional and helpful")
        expertise = personality.get("expertise", "general assistance")

        base_prompt = f"""
You are {assistant_name} with the following characteristics:
- Tone: {tone}
- Expertise: {expertise}
- Be helpful, accurate, and maintain conversation context
- Provide concise but informative responses
"""
        return base_prompt.strip()

    async def _generate_complete_response(
        self, messages: List[Dict[str, str]], context: ConversationContext
    ) -> AIResponse:
        """Generate complete AI response"""
        try:
            response = await self.client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            content = response.choices[0].message.content

            # Create structured response
            ai_response = AIResponse(
                content=content,
                context_used=[],
                confidence_score=0.9,
                response_type="direct",
                metadata={
                    "model_used": self.default_model,
                    "tokens_used": response.usage.total_tokens,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            logger.info(f"Generated AI response: {len(content)} characters")
            return ai_response

        except Exception as e:
            logger.error(f"Error in complete response generation: {str(e)}")
            raise

    async def _stream_response(
        self, messages: List[Dict[str, str]], context: ConversationContext
    ) -> AsyncGenerator[str, None]:
        """Stream AI response for real-time chat"""
        try:
            stream = await self.client.chat.completions.create(
                model=self.streaming_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            yield f"Error generating response: {str(e)}"

    async def create_conversation_context(
        self,
        chatbot_id: str,
        conversation_id: str,
        user_id: str,
        personality_config: Optional[Dict[str, Any]] = None,
    ) -> ConversationContext:
        """Create conversation context for new chat session"""

        # Default personality if not provided
        default_personality = {
            "name": "Pixel AI Assistant",
            "tone": "friendly and professional",
            "expertise": "general assistance",
        }

        personality = personality_config or default_personality

        context = ConversationContext(
            chatbot_id=chatbot_id,
            conversation_id=conversation_id,
            user_id=user_id,
            personality=personality,
            context_history=[],
            metadata={"created_at": datetime.utcnow().isoformat()},
        )

        logger.info(f"Created conversation context for chatbot {chatbot_id}")
        return context

    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI service health"""
        try:
            # Test simple API call
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )

            return {
                "status": "healthy",
                "api_accessible": True,
                "model_available": True,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
