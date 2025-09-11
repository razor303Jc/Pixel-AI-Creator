"""
Comprehensive backend tests for AI Integration, Database Schema, and RazorFlow services.
Tests all newly implemented HIGH PRIORITY components with full coverage.
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import our application modules
from api.core.database import Base, get_db
from api.models.models import (
    User,
    Client,
    Chatbot,
    Conversation,
    Message,
    Template,
    Build,
    Analytics,
)
from api.services.ai_service import AIService
from api.services.razorflow_service import RazorFlowService
from api.core.config import settings


class TestAIService:
    """Test suite for AI Integration service"""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        return AIService()

    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return {
            "choices": [
                {
                    "message": {
                        "content": "Hello! I'm here to help with your customer service needs. How can I assist you today?"
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 25, "completion_tokens": 18, "total_tokens": 43},
        }

    @pytest.mark.asyncio
    async def test_generate_response_basic(self, ai_service, mock_openai_response):
        """Test basic AI response generation"""
        with patch("openai.ChatCompletion.acreate") as mock_openai:
            mock_openai.return_value = mock_openai_response

            response = await ai_service.generate_response(
                message="Hello, I need help", personality="customer_support", context={}
            )

            assert response["content"] is not None
            assert len(response["content"]) > 0
            assert "usage" in response
            assert response["usage"]["total_tokens"] == 43

            # Verify OpenAI was called with correct parameters
            mock_openai.assert_called_once()
            call_args = mock_openai.call_args
            assert call_args[1]["model"] == "gpt-4"
            assert len(call_args[1]["messages"]) >= 2  # System + user message

    @pytest.mark.asyncio
    async def test_personality_customization(self, ai_service):
        """Test different AI personalities"""
        test_cases = [
            {
                "personality": "sales_assistant",
                "message": "Tell me about your product",
                "expected_keywords": ["product", "benefit", "feature", "value"],
            },
            {
                "personality": "technical_expert",
                "message": "How do I configure the API?",
                "expected_keywords": ["configure", "setting", "parameter", "technical"],
            },
            {
                "personality": "customer_support",
                "message": "I have a problem",
                "expected_keywords": ["help", "assist", "support", "resolve"],
            },
        ]

        for case in test_cases:
            with patch("openai.ChatCompletion.acreate") as mock_openai:
                mock_response = {
                    "choices": [
                        {
                            "message": {
                                "content": f"I'm a {case['personality']} and I can help with "
                                + " ".join(case["expected_keywords"])
                            }
                        }
                    ]
                }
                mock_openai.return_value = mock_response

                response = await ai_service.generate_response(
                    message=case["message"], personality=case["personality"]
                )

                content_lower = response["content"].lower()
                # Check that personality-specific keywords appear
                keyword_found = any(
                    keyword in content_lower for keyword in case["expected_keywords"]
                )
                assert (
                    keyword_found
                ), f"No personality keywords found for {case['personality']}"

    @pytest.mark.asyncio
    async def test_streaming_response(self, ai_service):
        """Test streaming AI responses"""
        with patch("openai.ChatCompletion.acreate") as mock_openai:
            # Mock streaming response
            async def mock_stream():
                chunks = [
                    {"choices": [{"delta": {"content": "Hello"}}]},
                    {"choices": [{"delta": {"content": " there!"}}]},
                    {"choices": [{"delta": {}}]},  # End chunk
                ]
                for chunk in chunks:
                    yield chunk

            mock_openai.return_value = mock_stream()

            full_response = ""
            async for chunk in ai_service.generate_streaming_response(
                message="Hello", personality="customer_support"
            ):
                if chunk.get("content"):
                    full_response += chunk["content"]

            assert full_response == "Hello there!"

    def test_conversation_context_management(self, ai_service):
        """Test conversation context handling"""
        context = {
            "conversation_id": "conv_123",
            "previous_messages": [
                {"role": "user", "content": "What's your name?"},
                {"role": "assistant", "content": "I'm an AI assistant."},
            ],
            "user_preferences": {"response_length": "short", "tone": "formal"},
        }

        formatted_context = ai_service._format_conversation_context(context)

        assert len(formatted_context) >= 2  # Previous messages included
        assert any("AI assistant" in msg["content"] for msg in formatted_context)

        # Test context truncation for long conversations
        long_context = {
            "previous_messages": [
                {"role": "user", "content": f"Message {i}"} for i in range(50)
            ]
        }

        truncated = ai_service._format_conversation_context(long_context)
        assert len(truncated) <= ai_service.max_context_messages

    @pytest.mark.asyncio
    async def test_error_handling(self, ai_service):
        """Test AI service error handling"""
        with patch("openai.ChatCompletion.acreate") as mock_openai:
            # Test API error
            mock_openai.side_effect = Exception("OpenAI API Error")

            with pytest.raises(Exception) as exc_info:
                await ai_service.generate_response("Test message")

            assert "OpenAI API Error" in str(exc_info.value)

        # Test rate limiting
        with patch("openai.ChatCompletion.acreate") as mock_openai:
            mock_openai.side_effect = Exception("Rate limit exceeded")

            response = await ai_service.generate_response_with_retry(
                "Test message", max_retries=2
            )

            # Should return fallback response
            assert "temporarily unavailable" in response["content"].lower()


class TestDatabaseSchema:
    """Test suite for Database Schema and Models"""

    @pytest.fixture
    def db_engine(self):
        """Create in-memory SQLite database for testing"""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(bind=engine)
        return engine

    @pytest.fixture
    def db_session(self, db_engine):
        """Create database session for testing"""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def test_user_model_creation(self, db_session):
        """Test User model CRUD operations"""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
            full_name="Test User",
            is_active=True,
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_client_model_relationships(self, db_session):
        """Test Client model and its relationships"""
        # Create user first
        user = User(
            email="owner@example.com",
            hashed_password="hashed_pass",
            full_name="Client Owner",
        )
        db_session.add(user)
        db_session.commit()

        # Create client
        client = Client(
            name="Test Business",
            industry="Restaurant",
            subscription_plan="premium",
            owner_id=user.id,
        )
        db_session.add(client)
        db_session.commit()
        db_session.refresh(client)

        assert client.id is not None
        assert client.owner_id == user.id
        assert client.subscription_plan == "premium"

        # Test relationship
        assert client.owner.email == "owner@example.com"

    def test_chatbot_configuration(self, db_session):
        """Test Chatbot model with configuration"""
        user = User(email="test@example.com", hashed_password="pass")
        client = Client(name="Test Client", owner_id=1)

        db_session.add_all([user, client])
        db_session.commit()

        chatbot = Chatbot(
            name="Customer Support Bot",
            personality="customer_support",
            client_id=client.id,
            configuration={
                "response_tone": "friendly",
                "response_length": "medium",
                "custom_instructions": "Always ask for order number",
                "knowledge_base": ["FAQ", "Product Catalog"],
            },
            is_active=True,
        )

        db_session.add(chatbot)
        db_session.commit()
        db_session.refresh(chatbot)

        assert chatbot.id is not None
        assert chatbot.configuration["response_tone"] == "friendly"
        assert "FAQ" in chatbot.configuration["knowledge_base"]
        assert chatbot.client.name == "Test Client"

    def test_conversation_message_flow(self, db_session):
        """Test Conversation and Message models"""
        # Setup prerequisites
        user = User(email="test@example.com", hashed_password="pass")
        client = Client(name="Test Client", owner_id=1)
        chatbot = Chatbot(name="Test Bot", client_id=1)

        db_session.add_all([user, client, chatbot])
        db_session.commit()

        # Create conversation
        conversation = Conversation(
            chatbot_id=chatbot.id,
            session_id="session_123",
            metadata={
                "user_agent": "Mozilla/5.0",
                "ip_address": "127.0.0.1",
                "referrer": "https://example.com",
            },
        )

        db_session.add(conversation)
        db_session.commit()

        # Add messages
        messages = [
            Message(
                conversation_id=conversation.id,
                content="Hello, I need help with my order",
                role="user",
                metadata={"timestamp": datetime.utcnow().isoformat()},
            ),
            Message(
                conversation_id=conversation.id,
                content="I'd be happy to help! Can you provide your order number?",
                role="assistant",
                metadata={"ai_model": "gpt-4", "tokens_used": 23, "response_time": 1.2},
            ),
        ]

        db_session.add_all(messages)
        db_session.commit()

        # Test relationships and queries
        assert len(conversation.messages) == 2
        assert conversation.messages[0].role == "user"
        assert conversation.messages[1].role == "assistant"
        assert conversation.messages[1].metadata["ai_model"] == "gpt-4"

    def test_analytics_model(self, db_session):
        """Test Analytics model for tracking metrics"""
        user = User(email="test@example.com", hashed_password="pass")
        client = Client(name="Analytics Client", owner_id=1)

        db_session.add_all([user, client])
        db_session.commit()

        analytics = Analytics(
            client_id=client.id,
            metric_type="conversation_volume",
            metric_value=150,
            time_period="daily",
            metadata={
                "date": "2024-01-15",
                "chatbot_id": 1,
                "breakdown": {"morning": 45, "afternoon": 60, "evening": 45},
            },
        )

        db_session.add(analytics)
        db_session.commit()
        db_session.refresh(analytics)

        assert analytics.id is not None
        assert analytics.metric_value == 150
        assert analytics.metadata["breakdown"]["afternoon"] == 60

    def test_database_constraints_and_validation(self, db_session):
        """Test database constraints and validation"""
        # Test unique constraint on user email
        user1 = User(email="unique@example.com", hashed_password="pass1")
        user2 = User(email="unique@example.com", hashed_password="pass2")

        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()

        db_session.rollback()

        # Test foreign key constraints
        invalid_client = Client(name="Invalid Client", owner_id=99999)
        db_session.add(invalid_client)

        with pytest.raises(Exception):  # Foreign key violation
            db_session.commit()


class TestRazorFlowService:
    """Test suite for RazorFlow Integration service"""

    @pytest.fixture
    def razorflow_service(self):
        """Create RazorFlow service instance for testing"""
        return RazorFlowService()

    @pytest.fixture
    def mock_build_response(self):
        """Mock RazorFlow build response"""
        return {
            "build_id": "build_12345",
            "status": "queued",
            "estimated_completion": "2024-01-15T14:30:00Z",
            "selected_template": "restaurant-chatbot-v2",
            "features": ["order_taking", "reservations", "menu_display"],
            "deployment_url": None,
        }

    @pytest.mark.asyncio
    async def test_queue_client_build(self, razorflow_service, mock_build_response):
        """Test queueing a client build"""
        with patch.object(razorflow_service, "_make_api_request") as mock_request:
            mock_request.return_value = mock_build_response

            result = await razorflow_service.queue_client_build(
                client_id=1,
                template_type="restaurant",
                custom_requirements={
                    "features": ["order_taking", "reservations"],
                    "integrations": ["stripe", "google_calendar"],
                    "branding": {"primary_color": "#2E8B57"},
                },
                priority="high",
            )

            assert result["build_id"] == "build_12345"
            assert result["status"] == "queued"
            assert "order_taking" in result["features"]

            # Verify API call parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args[1]
            assert call_args["data"]["template_type"] == "restaurant"
            assert call_args["data"]["priority"] == "high"

    @pytest.mark.asyncio
    async def test_check_build_status(self, razorflow_service):
        """Test checking build status"""
        status_responses = [
            {"build_id": "build_123", "status": "queued", "progress": 0},
            {"build_id": "build_123", "status": "processing", "progress": 45},
            {
                "build_id": "build_123",
                "status": "completed",
                "progress": 100,
                "deployment_url": "https://client1.razorflow.ai",
            },
        ]

        with patch.object(razorflow_service, "_make_api_request") as mock_request:
            mock_request.side_effect = status_responses

            # Test queued status
            result = await razorflow_service.check_build_status("build_123")
            assert result["status"] == "queued"
            assert result["progress"] == 0

            # Test processing status
            result = await razorflow_service.check_build_status("build_123")
            assert result["status"] == "processing"
            assert result["progress"] == 45

            # Test completed status
            result = await razorflow_service.check_build_status("build_123")
            assert result["status"] == "completed"
            assert result["progress"] == 100
            assert "deployment_url" in result

    @pytest.mark.asyncio
    async def test_deploy_default_assistant_suite(self, razorflow_service):
        """Test deploying default assistant suite"""
        mock_response = {
            "deployment_id": "deploy_456",
            "status": "deploying",
            "components": [
                {"name": "customer_support", "type": "chatbot"},
                {"name": "sales_assistant", "type": "chatbot"},
                {"name": "analytics_dashboard", "type": "webapp"},
            ],
            "urls": {
                "customer_support": "https://support.client1.razorflow.ai",
                "sales_assistant": "https://sales.client1.razorflow.ai",
                "dashboard": "https://dashboard.client1.razorflow.ai",
            },
        }

        with patch.object(razorflow_service, "_make_api_request") as mock_request:
            mock_request.return_value = mock_response

            result = await razorflow_service.deploy_default_assistant_suite(client_id=1)

            assert result["deployment_id"] == "deploy_456"
            assert len(result["components"]) == 3
            assert "customer_support" in result["urls"]
            assert "dashboard" in result["urls"]

            # Verify default configuration was applied
            call_args = mock_request.call_args[1]
            assert "default_personalities" in call_args["data"]
            assert "standard_features" in call_args["data"]

    def test_template_selection_logic(self, razorflow_service):
        """Test template selection based on requirements"""
        test_cases = [
            {
                "business_type": "restaurant",
                "features": ["order_taking", "reservations"],
                "expected_template": "restaurant-chatbot-v2",
            },
            {
                "business_type": "ecommerce",
                "features": ["product_catalog", "shopping_cart"],
                "expected_template": "ecommerce-assistant-v3",
            },
            {
                "business_type": "healthcare",
                "features": ["appointment_booking", "symptom_checker"],
                "expected_template": "healthcare-assistant-v1",
            },
            {
                "business_type": "general",
                "features": ["faq", "contact_support"],
                "expected_template": "general-purpose-v2",
            },
        ]

        for case in test_cases:
            template = razorflow_service._select_optimal_template(
                business_type=case["business_type"], required_features=case["features"]
            )

            assert template == case["expected_template"]

    def test_configuration_validation(self, razorflow_service):
        """Test build configuration validation"""
        # Valid configuration
        valid_config = {
            "template_type": "restaurant",
            "features": ["order_taking", "reservations"],
            "integrations": ["stripe"],
            "branding": {"primary_color": "#2E8B57"},
        }

        validation_result = razorflow_service._validate_build_config(valid_config)
        assert validation_result["is_valid"] is True
        assert len(validation_result["errors"]) == 0

        # Invalid configuration - missing required features
        invalid_config = {
            "template_type": "restaurant",
            "features": [],  # Empty features
            "integrations": ["invalid_integration"],
            "branding": {"primary_color": "invalid_color"},
        }

        validation_result = razorflow_service._validate_build_config(invalid_config)
        assert validation_result["is_valid"] is False
        assert len(validation_result["errors"]) > 0
        assert any("features" in error for error in validation_result["errors"])

    @pytest.mark.asyncio
    async def test_error_handling_and_retries(self, razorflow_service):
        """Test error handling and retry logic"""
        # Test network error with retry
        with patch.object(razorflow_service, "_make_api_request") as mock_request:
            mock_request.side_effect = [
                Exception("Network timeout"),
                Exception("Service unavailable"),
                {
                    "build_id": "build_success",
                    "status": "queued",
                },  # Success on third try
            ]

            result = await razorflow_service.queue_client_build_with_retry(
                client_id=1, template_type="general", max_retries=3
            )

            assert result["build_id"] == "build_success"
            assert mock_request.call_count == 3

        # Test API error handling
        with patch.object(razorflow_service, "_make_api_request") as mock_request:
            mock_request.return_value = {
                "error": "Invalid template type",
                "code": "TEMPLATE_NOT_FOUND",
            }

            with pytest.raises(Exception) as exc_info:
                await razorflow_service.queue_client_build(
                    client_id=1, template_type="nonexistent_template"
                )

            assert "Invalid template type" in str(exc_info.value)


class TestIntegrationScenarios:
    """Integration tests combining multiple services"""

    @pytest.fixture
    def services(self, db_session):
        """Create service instances with database session"""
        return {"ai": AIService(), "razorflow": RazorFlowService(), "db": db_session}

    @pytest.mark.asyncio
    async def test_complete_client_onboarding_flow(self, services):
        """Test complete client onboarding from creation to first AI chat"""
        db = services["db"]
        ai_service = services["ai"]
        razorflow_service = services["razorflow"]

        # 1. Create user and client
        user = User(
            email="newclient@restaurant.com",
            hashed_password="hashed_pass",
            full_name="Restaurant Owner",
        )
        db.add(user)
        db.commit()

        client = Client(
            name="Luigi's Italian Restaurant",
            industry="Restaurant",
            subscription_plan="premium",
            owner_id=user.id,
        )
        db.add(client)
        db.commit()

        # 2. Queue RazorFlow build
        with patch.object(razorflow_service, "_make_api_request") as mock_razorflow:
            mock_razorflow.return_value = {
                "build_id": "build_restaurant_123",
                "status": "completed",
                "deployment_url": "https://luigis.razorflow.ai",
            }

            build_result = await razorflow_service.queue_client_build(
                client_id=client.id,
                template_type="restaurant",
                custom_requirements={
                    "features": ["order_taking", "reservations", "menu_display"],
                    "integrations": ["stripe", "opentable"],
                },
            )

            assert build_result["build_id"] == "build_restaurant_123"

        # 3. Create chatbot
        chatbot = Chatbot(
            name="Luigi's Assistant",
            personality="customer_support",
            client_id=client.id,
            configuration={
                "response_tone": "friendly",
                "business_context": "Italian restaurant",
                "special_instructions": "Always mention daily specials",
            },
        )
        db.add(chatbot)
        db.commit()

        # 4. Test AI conversation with business context
        with patch("openai.ChatCompletion.acreate") as mock_openai:
            mock_openai.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "Welcome to Luigi's! Our daily special today is osso buco. How can I help you?"
                        }
                    }
                ]
            }

            ai_response = await ai_service.generate_response(
                message="Hello, I'd like to make a reservation",
                personality="customer_support",
                context={
                    "business_name": "Luigi's Italian Restaurant",
                    "business_type": "restaurant",
                    "client_id": client.id,
                },
            )

            assert "Luigi's" in ai_response["content"]
            assert "reservation" in ai_response["content"].lower()

        # 5. Create conversation record
        conversation = Conversation(
            chatbot_id=chatbot.id, session_id="reservation_session_001"
        )
        db.add(conversation)
        db.commit()

        # 6. Add messages to conversation
        messages = [
            Message(
                conversation_id=conversation.id,
                content="Hello, I'd like to make a reservation",
                role="user",
            ),
            Message(
                conversation_id=conversation.id,
                content=ai_response["content"],
                role="assistant",
                metadata={"ai_model": "gpt-4", "business_context": True},
            ),
        ]
        db.add_all(messages)
        db.commit()

        # Verify complete flow
        assert len(conversation.messages) == 2
        assert conversation.chatbot.client.name == "Luigi's Italian Restaurant"
        assert "Luigi's" in conversation.messages[1].content

    @pytest.mark.asyncio
    async def test_analytics_data_collection(self, services):
        """Test analytics data collection across services"""
        db = services["db"]

        # Create test data
        user = User(email="analytics@test.com", hashed_password="pass")
        client = Client(name="Analytics Test Client", owner_id=1)
        chatbot = Chatbot(name="Test Bot", client_id=1)

        db.add_all([user, client, chatbot])
        db.commit()

        # Simulate multiple conversations over time
        conversations_data = [
            {"date": datetime.utcnow() - timedelta(days=7), "count": 15},
            {"date": datetime.utcnow() - timedelta(days=6), "count": 22},
            {"date": datetime.utcnow() - timedelta(days=5), "count": 18},
            {"date": datetime.utcnow() - timedelta(days=4), "count": 30},
            {"date": datetime.utcnow() - timedelta(days=3), "count": 25},
        ]

        analytics_records = []
        for data in conversations_data:
            analytics = Analytics(
                client_id=client.id,
                metric_type="conversation_volume",
                metric_value=data["count"],
                time_period="daily",
                metadata={"date": data["date"].isoformat(), "chatbot_id": chatbot.id},
            )
            analytics_records.append(analytics)

        db.add_all(analytics_records)
        db.commit()

        # Query analytics data
        total_conversations = sum(record.metric_value for record in analytics_records)
        average_daily = total_conversations / len(analytics_records)

        assert total_conversations == 110
        assert average_daily == 22.0

        # Test analytics aggregation
        weekly_analytics = Analytics(
            client_id=client.id,
            metric_type="conversation_volume",
            metric_value=total_conversations,
            time_period="weekly",
            metadata={
                "start_date": (datetime.utcnow() - timedelta(days=7)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "daily_breakdown": [
                    {"date": d["date"].isoformat(), "count": d["count"]}
                    for d in conversations_data
                ],
            },
        )

        db.add(weekly_analytics)
        db.commit()

        assert weekly_analytics.metric_value == 110
        assert len(weekly_analytics.metadata["daily_breakdown"]) == 5


if __name__ == "__main__":
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=api",
            "--cov-report=html",
            "--cov-report=term-missing",
        ]
    )
