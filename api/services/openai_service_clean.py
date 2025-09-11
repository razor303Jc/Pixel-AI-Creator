"""
OpenAI Service for AI Integration Implementation

This service provides:
- OpenAI API integration with conversation context management
- Streaming response support for real-time chat
- Personality-based response generation
- Template-driven conversation flows
- Context-aware response generation with ChromaDB integration
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
    response_type: str  # "direct", "context_enhanced", "template_based"
    metadata: Dict[str, Any]


class OpenAIService:
    """Enhanced OpenAI service for AI integration"""

    def __init__(self):
        """Initialize OpenAI service with configuration"""
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.vector_service = VectorStorageService(settings)
        self.default_model = "gpt-4"
        self.streaming_model = "gpt-4"
        self.embedding_model = "text-embedding-ada-002"

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
        """
        Generate AI response with context awareness
        """
        try:
            # Enhance context with knowledge base if enabled
            enhanced_context = context
            if use_knowledge_base:
                enhanced_context = await self._enhance_context_with_knowledge(
                    message, context
                )

            # Build conversation messages
            messages = await self._build_conversation_messages(
                message, enhanced_context
            )

            # Generate response
            if stream:
                return self._stream_response(messages, enhanced_context)
            else:
                return await self._generate_complete_response(
                    messages, enhanced_context
                )

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            raise

    async def _enhance_context_with_knowledge(
        self, message: str, context: ConversationContext
    ) -> ConversationContext:
        """Enhance context using RAG with ChromaDB knowledge base"""
        try:
            # Search for relevant context in knowledge base
            search_results = await self.vector_service.similarity_search(
                chatbot_id=context.chatbot_id, query=message, n_results=3
            )

            # Extract relevant knowledge
            knowledge_context = []
            for result in search_results.get("results", []):
                knowledge_context.append(
                    {
                        "content": result.get("document", ""),
                        "similarity": result.get("distance", 0.0),
                        "metadata": result.get("metadata", {}),
                    }
                )

            # Update context with knowledge
            enhanced_context = ConversationContext(
                chatbot_id=context.chatbot_id,
                conversation_id=context.conversation_id,
                user_id=context.user_id,
                personality=context.personality,
                context_history=context.context_history,
                knowledge_base=knowledge_context,
                metadata=context.metadata,
            )

            logger.info(
                f"Enhanced context with {len(knowledge_context)} knowledge entries"
            )
            return enhanced_context

        except Exception as e:
            logger.warning(f"Failed to enhance context with knowledge base: {str(e)}")
            return context

    async def _build_conversation_messages(
        self, message: str, context: ConversationContext
    ) -> List[Dict[str, str]]:
        """Build conversation messages for OpenAI API"""
        messages = []

        # System message with personality
        system_prompt = self._build_system_prompt(context)
        messages.append({"role": "system", "content": system_prompt})

        # Add knowledge base context if available
        if context.knowledge_base:
            knowledge_content = self._format_knowledge_context(context.knowledge_base)
            knowledge_msg = f"Relevant knowledge base information:\n{knowledge_content}"
            messages.append({"role": "system", "content": knowledge_msg})

        # Add conversation history (limited to context window)
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
        style = personality.get("style", "conversational")
        expertise = personality.get("expertise", "general assistance")
        behavior = personality.get(
            "behavior_guidelines", "Be helpful, accurate, and respectful"
        )
        domain = personality.get("domain", "general")
        preferences = personality.get("user_preferences", "not specified")

        base_prompt = f"""
You are {assistant_name} with the following characteristics:

PERSONALITY:
- Tone: {tone}
- Style: {style}
- Expertise: {expertise}

BEHAVIOR:
- {behavior}

CONTEXT:
- You are assisting in a {domain} context
- User preferences: {preferences}

INSTRUCTIONS:
- Provide accurate, helpful responses
- Maintain the specified personality traits
- Use knowledge base information when relevant
- Keep responses concise but informative
"""

        return base_prompt.strip()

    def _format_knowledge_context(self, knowledge_base: List[Dict[str, Any]]) -> str:
        """Format knowledge base entries for context"""
        formatted_entries = []

        for entry in knowledge_base:
            content = entry.get("content", "")
            similarity = entry.get("similarity", 0.0)

            # Only include high-relevance entries
            if content and similarity > 0.7:
                formatted_entries.append(f"- {content[:200]}...")

        if formatted_entries:
            return "\n".join(formatted_entries)
        else:
            return "No relevant context found."

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
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1,
            )

            content = response.choices[0].message.content

            # Extract system messages for context tracking
            system_messages = [
                msg["content"][:50] + "..."
                for msg in messages
                if msg["role"] == "system"
            ]

            # Determine response type
            response_type = "context_enhanced" if context.knowledge_base else "direct"

            # Create structured response
            ai_response = AIResponse(
                content=content,
                context_used=system_messages,
                confidence_score=0.9,
                response_type=response_type,
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
            "style": "conversational",
            "expertise": "general assistance",
            "behavior_guidelines": "Be helpful, accurate, and engage users",
            "domain": "customer support",
            "user_preferences": "not specified",
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

    async def update_conversation_context(
        self, context: ConversationContext, user_message: str, ai_response: str
    ) -> ConversationContext:
        """Update conversation context with new message exchange"""

        # Add to context history
        context.context_history.append(
            {
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Store in knowledge base for future context
        try:
            await self.vector_service.store_conversation_embedding(
                chatbot_id=context.chatbot_id,
                conversation_id=context.conversation_id,
                message=user_message,
                response=ai_response,
                metadata={
                    "user_id": context.user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        except Exception as e:
            logger.warning(f"Failed to store conversation embedding: {str(e)}")

        logger.info(
            f"Updated conversation context: {len(context.context_history)} messages"
        )
        return context

    async def generate_personality_config(
        self, client_data: Dict[str, Any], assistant_type: str = "chatbot"
    ) -> Dict[str, Any]:
        """Generate personality configuration based on client data"""

        company_name = client_data.get("name", "Your Company")
        industry = client_data.get("industry", "business")
        description = client_data.get("description", "")

        # Build personality generation prompt
        prompt = f"""
Create a chatbot personality configuration for {company_name} in the {industry} industry.

Company Description: {description}

Generate a JSON configuration with the following structure:
{{
    "name": "Company Bot Name",
    "tone": "professional/friendly/casual tone description",
    "style": "conversational style description",
    "expertise": "area of expertise based on industry",
    "behavior_guidelines": "specific behavior guidelines",
    "domain": "business domain",
    "user_preferences": "target user preferences"
}}

Make it engaging and appropriate for the industry and company.
"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=500,
            )

            personality_text = response.choices[0].message.content
            personality_config = json.loads(personality_text)

            logger.info(f"Generated personality config for {company_name}")
            return personality_config

        except Exception as e:
            logger.warning(f"Failed to generate personality config: {str(e)}")

            # Return default configuration
            return {
                "name": f"{company_name} Assistant",
                "tone": "professional and helpful",
                "style": "conversational",
                "expertise": f"{industry} industry assistance",
                "behavior_guidelines": "Be helpful, professional, knowledgeable",
                "domain": industry,
                "user_preferences": "professional business interactions",
            }

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
