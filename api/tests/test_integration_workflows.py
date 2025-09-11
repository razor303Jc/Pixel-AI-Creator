"""
Integration tests for Pixel AI Creator workflows.

This test suite covers:
- Complete business workflows from start to finish
- Cross-service integration testing
- Data consistency across operations
- Performance under realistic conditions
- Error recovery and rollback scenarios
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime, timedelta
import threading
import time
import uuid

# Import the FastAPI app and dependencies
from main import app
from core.database import get_db, Base
from core.auth import get_current_user
from models.user import User, UserRole
from models.client import Client
from models.chatbot import Chatbot, ChatbotType, ChatbotStatus
from models.conversation import Conversation, ConversationStatus
from models.message import Message, MessageRole

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Test client setup
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def business_user():
    """Create a business user."""
    return {
        "email": "business@company.com",
        "password": "businesspass123",
        "full_name": "Business Manager",
        "role": "user",
    }


@pytest.fixture
def enterprise_client():
    """Create an enterprise client."""
    return {
        "name": "TechCorp Enterprise",
        "email": "contact@techcorp.com",
        "industry": "Technology",
        "description": "Large enterprise with complex requirements",
        "requirements": "Multi-language support, high availability, custom integrations",
    }


@pytest.fixture
def complex_chatbot():
    """Create a complex chatbot configuration."""
    return {
        "name": "Enterprise Support Bot",
        "type": "advanced",
        "complexity": "enterprise",
        "requirements": "24/7 support, multilingual, API integrations",
        "industry": "Technology",
        "personality": "Professional, knowledgeable, efficient",
        "capabilities": ["NLP", "sentiment_analysis", "escalation"],
        "languages": ["en", "es", "fr", "de"],
    }


class TestBusinessWorkflows:
    """Test complete business workflows."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_complete_onboarding_workflow(
        self, test_db, business_user, enterprise_client, complex_chatbot
    ):
        """Test complete client onboarding workflow."""
        headers = self.get_auth_headers(test_db, business_user)

        # Step 1: User registration and profile setup
        profile_update = {
            "company": "Business Solutions Inc",
            "phone": "+1-555-0123",
            "preferences": {"notifications": True, "language": "en"},
        }
        profile_response = client.put(
            "/api/auth/profile", headers=headers, json=profile_update
        )
        assert profile_response.status_code == 200

        # Step 2: Create enterprise client
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        assert client_response.status_code == 201
        client_id = client_response.json()["id"]

        # Step 3: Create complex chatbot with enterprise features
        chatbot_data = {**complex_chatbot, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        assert chatbot_response.status_code == 201
        chatbot_id = chatbot_response.json()["id"]

        # Step 4: Configure chatbot settings
        settings_data = {
            "enable_analytics": True,
            "auto_escalation": True,
            "response_timeout": 30,
            "max_conversation_length": 100,
        }
        settings_response = client.put(
            f"/api/chatbots/{chatbot_id}/settings", headers=headers, json=settings_data
        )
        assert settings_response.status_code == 200

        # Step 5: Deploy chatbot
        deploy_response = client.post(
            f"/api/chatbots/{chatbot_id}/deploy", headers=headers
        )
        assert deploy_response.status_code == 200

        # Step 6: Verify deployment status
        status_response = client.get(
            f"/api/chatbots/{chatbot_id}/status", headers=headers
        )
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["status"] in ["deployed", "deploying"]

        # Step 7: Create initial conversation to test functionality
        conversation_data = {
            "chatbot_id": chatbot_id,
            "title": "Enterprise Onboarding Test",
            "initial_message": "Hello, I need assistance with enterprise features",
        }
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conversation_data
        )
        assert conv_response.status_code == 201
        conversation_id = conv_response.json()["id"]

        # Step 8: Test conversation flow
        messages = [
            {"content": "What enterprise features are available?", "role": "user"},
            {"content": "I need help with API integration", "role": "user"},
            {"content": "Can you escalate this to a human agent?", "role": "user"},
        ]

        for message in messages:
            msg_response = client.post(
                f"/api/conversations/{conversation_id}/messages",
                headers=headers,
                json=message,
            )
            assert msg_response.status_code == 201

        # Step 9: Generate analytics report
        analytics_response = client.get(
            f"/api/analytics/chatbot/{chatbot_id}/summary", headers=headers
        )
        assert analytics_response.status_code == 200

        # Step 10: Verify complete workflow data consistency
        final_client = client.get(f"/api/clients/{client_id}", headers=headers)
        final_chatbot = client.get(f"/api/chatbots/{chatbot_id}", headers=headers)
        final_conversation = client.get(
            f"/api/conversations/{conversation_id}", headers=headers
        )

        assert final_client.status_code == 200
        assert final_chatbot.status_code == 200
        assert final_conversation.status_code == 200

        # Verify relationships
        assert final_chatbot.json()["client_id"] == client_id
        assert final_conversation.json()["chatbot_id"] == chatbot_id

    def test_multi_client_management_workflow(self, test_db, business_user):
        """Test managing multiple clients simultaneously."""
        headers = self.get_auth_headers(test_db, business_user)

        # Create multiple clients
        clients_data = [
            {
                "name": "Startup Client",
                "email": "startup@example.com",
                "industry": "Fintech",
            },
            {"name": "SMB Client", "email": "smb@example.com", "industry": "Retail"},
            {
                "name": "Enterprise Client",
                "email": "enterprise@example.com",
                "industry": "Healthcare",
            },
        ]

        client_ids = []
        for client_data in clients_data:
            response = client.post("/api/clients", headers=headers, json=client_data)
            assert response.status_code == 201
            client_ids.append(response.json()["id"])

        # Create chatbots for each client
        chatbot_configs = [
            {"name": "Startup Bot", "type": "basic", "complexity": "simple"},
            {"name": "SMB Bot", "type": "standard", "complexity": "moderate"},
            {"name": "Enterprise Bot", "type": "advanced", "complexity": "enterprise"},
        ]

        chatbot_ids = []
        for i, (client_id, config) in enumerate(zip(client_ids, chatbot_configs)):
            chatbot_data = {
                **config,
                "client_id": client_id,
                "industry": clients_data[i]["industry"],
            }
            response = client.post("/api/chatbots", headers=headers, json=chatbot_data)
            assert response.status_code == 201
            chatbot_ids.append(response.json()["id"])

        # Create conversations for each chatbot
        conversation_ids = []
        for chatbot_id in chatbot_ids:
            conv_data = {
                "chatbot_id": chatbot_id,
                "title": f"Test conversation for chatbot {chatbot_id}",
            }
            response = client.post(
                "/api/conversations", headers=headers, json=conv_data
            )
            assert response.status_code == 201
            conversation_ids.append(response.json()["id"])

        # Verify all relationships are maintained
        for i, (client_id, chatbot_id, conv_id) in enumerate(
            zip(client_ids, chatbot_ids, conversation_ids)
        ):
            client_response = client.get(f"/api/clients/{client_id}", headers=headers)
            chatbot_response = client.get(
                f"/api/chatbots/{chatbot_id}", headers=headers
            )
            conv_response = client.get(f"/api/conversations/{conv_id}", headers=headers)

            assert client_response.status_code == 200
            assert chatbot_response.status_code == 200
            assert conv_response.status_code == 200

            assert chatbot_response.json()["client_id"] == client_id
            assert conv_response.json()["chatbot_id"] == chatbot_id

        # Test bulk operations
        bulk_update_data = {"status": "active"}
        for chatbot_id in chatbot_ids:
            response = client.patch(
                f"/api/chatbots/{chatbot_id}/status",
                headers=headers,
                json=bulk_update_data,
            )
            assert response.status_code == 200

    def test_conversation_lifecycle_workflow(
        self, test_db, business_user, enterprise_client, complex_chatbot
    ):
        """Test complete conversation lifecycle."""
        headers = self.get_auth_headers(test_db, business_user)

        # Setup client and chatbot
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        client_id = client_response.json()["id"]

        chatbot_data = {**complex_chatbot, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = chatbot_response.json()["id"]

        # Start conversation
        conversation_data = {
            "chatbot_id": chatbot_id,
            "title": "Lifecycle Test Conversation",
            "metadata": {"customer_id": "CUST_123", "priority": "high"},
        }
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conversation_data
        )
        conversation_id = conv_response.json()["id"]

        # Simulate realistic conversation flow
        conversation_flow = [
            {"content": "Hello, I need help with my account", "role": "user"},
            {
                "content": "I'd be happy to help you with your account. What specific issue are you experiencing?",
                "role": "assistant",
            },
            {"content": "I can't access my premium features", "role": "user"},
            {
                "content": "Let me check your account status. Can you provide your customer ID?",
                "role": "assistant",
            },
            {"content": "My customer ID is CUST_123", "role": "user"},
            {
                "content": "Thank you. I can see your account. Let me escalate this to our technical team.",
                "role": "assistant",
            },
            {"content": "How long will this take to resolve?", "role": "user"},
            {
                "content": "Our technical team typically responds within 2-4 hours for premium accounts.",
                "role": "assistant",
            },
        ]

        message_ids = []
        for message in conversation_flow:
            msg_response = client.post(
                f"/api/conversations/{conversation_id}/messages",
                headers=headers,
                json=message,
            )
            assert msg_response.status_code == 201
            message_ids.append(msg_response.json()["id"])

        # Test conversation status updates
        status_updates = ["active", "escalated", "resolved"]
        for status in status_updates:
            status_data = {"status": status, "notes": f"Conversation moved to {status}"}
            response = client.patch(
                f"/api/conversations/{conversation_id}/status",
                headers=headers,
                json=status_data,
            )
            assert response.status_code == 200

        # Test conversation analytics
        analytics_response = client.get(
            f"/api/conversations/{conversation_id}/analytics", headers=headers
        )
        assert analytics_response.status_code == 200
        analytics_data = analytics_response.json()
        assert "message_count" in analytics_data
        assert "duration" in analytics_data
        assert "sentiment_analysis" in analytics_data

        # Test conversation export
        export_response = client.get(
            f"/api/conversations/{conversation_id}/export", headers=headers
        )
        assert export_response.status_code == 200

        # Archive conversation
        archive_response = client.post(
            f"/api/conversations/{conversation_id}/archive", headers=headers
        )
        assert archive_response.status_code == 200


class TestDataConsistencyWorkflows:
    """Test data consistency across operations."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_cascade_delete_workflow(
        self, test_db, business_user, enterprise_client, complex_chatbot
    ):
        """Test cascade deletes maintain data consistency."""
        headers = self.get_auth_headers(test_db, business_user)

        # Create full hierarchy
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        client_id = client_response.json()["id"]

        chatbot_data = {**complex_chatbot, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = chatbot_response.json()["id"]

        # Create multiple conversations
        conversation_ids = []
        for i in range(3):
            conv_data = {"chatbot_id": chatbot_id, "title": f"Test Conversation {i+1}"}
            conv_response = client.post(
                "/api/conversations", headers=headers, json=conv_data
            )
            conversation_ids.append(conv_response.json()["id"])

        # Add messages to each conversation
        for conv_id in conversation_ids:
            for j in range(5):
                msg_data = {"content": f"Test message {j+1}", "role": "user"}
                client.post(
                    f"/api/conversations/{conv_id}/messages",
                    headers=headers,
                    json=msg_data,
                )

        # Verify all data exists
        chatbot_get = client.get(f"/api/chatbots/{chatbot_id}", headers=headers)
        assert chatbot_get.status_code == 200

        conversations_list = client.get(
            "/api/conversations", headers=headers, params={"chatbot_id": chatbot_id}
        )
        assert len(conversations_list.json()["conversations"]) == 3

        # Delete client (should cascade)
        delete_response = client.delete(f"/api/clients/{client_id}", headers=headers)
        assert delete_response.status_code == 200

        # Verify cascaded deletes
        chatbot_get_after = client.get(f"/api/chatbots/{chatbot_id}", headers=headers)
        assert chatbot_get_after.status_code == 404

        for conv_id in conversation_ids:
            conv_get_after = client.get(
                f"/api/conversations/{conv_id}", headers=headers
            )
            assert conv_get_after.status_code == 404

    def test_concurrent_access_consistency(
        self, test_db, business_user, enterprise_client
    ):
        """Test data consistency under concurrent access."""
        headers = self.get_auth_headers(test_db, business_user)

        # Create client
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        client_id = client_response.json()["id"]

        # Define concurrent operations
        results = []
        errors = []

        def create_chatbot(bot_name):
            try:
                chatbot_data = {
                    "name": f"Concurrent Bot {bot_name}",
                    "type": "standard",
                    "complexity": "moderate",
                    "client_id": client_id,
                    "industry": "Technology",
                }
                response = client.post(
                    "/api/chatbots", headers=headers, json=chatbot_data
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        def update_client():
            try:
                update_data = {
                    "description": f"Updated at {datetime.now().isoformat()}"
                }
                response = client.put(
                    f"/api/clients/{client_id}", headers=headers, json=update_data
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # Run concurrent operations
        threads = []

        # Create 5 chatbots concurrently
        for i in range(5):
            thread = threading.Thread(target=create_chatbot, args=(i,))
            threads.append(thread)

        # Update client concurrently
        for i in range(3):
            thread = threading.Thread(target=update_client)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert all(status in [200, 201] for status in results)

        # Verify data consistency
        final_client = client.get(f"/api/clients/{client_id}", headers=headers)
        assert final_client.status_code == 200

        chatbots_list = client.get(
            "/api/chatbots", headers=headers, params={"client_id": client_id}
        )
        assert chatbots_list.status_code == 200
        chatbots = chatbots_list.json()["chatbots"]
        assert len(chatbots) == 5  # All 5 chatbots should be created


class TestErrorRecoveryWorkflows:
    """Test error recovery and rollback scenarios."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @patch("services.ai_service.generate_response")
    def test_ai_service_failure_recovery(
        self,
        mock_ai_service,
        test_db,
        business_user,
        enterprise_client,
        complex_chatbot,
    ):
        """Test recovery when AI service fails."""
        headers = self.get_auth_headers(test_db, business_user)

        # Setup
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        client_id = client_response.json()["id"]

        chatbot_data = {**complex_chatbot, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = chatbot_response.json()["id"]

        conv_data = {"chatbot_id": chatbot_id, "title": "AI Failure Test"}
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conv_data
        )
        conversation_id = conv_response.json()["id"]

        # Mock AI service failure
        mock_ai_service.side_effect = Exception("AI service unavailable")

        # Send message that requires AI response
        message_data = {"content": "Hello, I need help", "role": "user"}
        msg_response = client.post(
            f"/api/conversations/{conversation_id}/messages",
            headers=headers,
            json=message_data,
        )

        # Should still accept the user message
        assert msg_response.status_code == 201

        # Check that failure is handled gracefully
        messages_response = client.get(
            f"/api/conversations/{conversation_id}/messages", headers=headers
        )
        assert messages_response.status_code == 200
        messages = messages_response.json()["messages"]

        # Should have user message and potentially a fallback response
        assert len(messages) >= 1
        assert messages[0]["role"] == "user"

    @patch("core.database.get_db")
    def test_database_failure_recovery(self, mock_db, test_db, business_user):
        """Test recovery when database fails."""
        # Mock database failure
        mock_db.side_effect = Exception("Database connection failed")

        # Attempt operations that should fail gracefully
        response = client.post("/api/auth/register", json=business_user)
        assert response.status_code == 500

        error_data = response.json()
        assert "detail" in error_data
        assert (
            "internal server error" in error_data["detail"].lower()
            or "database" in error_data["detail"].lower()
        )

    def test_partial_operation_rollback(
        self, test_db, business_user, enterprise_client
    ):
        """Test rollback of partial operations."""
        headers = self.get_auth_headers(test_db, business_user)

        # Create client
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        client_id = client_response.json()["id"]

        # Attempt to create chatbot with invalid data that should cause rollback
        invalid_chatbot_data = {
            "name": "Test Bot",
            "type": "invalid_type",  # Invalid type
            "client_id": client_id,
            "industry": "Technology",
        }

        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=invalid_chatbot_data
        )
        assert chatbot_response.status_code == 422  # Validation error

        # Verify client still exists and is unchanged
        client_get = client.get(f"/api/clients/{client_id}", headers=headers)
        assert client_get.status_code == 200

        # Verify no orphaned chatbot was created
        chatbots_list = client.get(
            "/api/chatbots", headers=headers, params={"client_id": client_id}
        )
        assert len(chatbots_list.json()["chatbots"]) == 0


class TestPerformanceWorkflows:
    """Test performance under realistic conditions."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_large_conversation_performance(
        self, test_db, business_user, enterprise_client, complex_chatbot
    ):
        """Test performance with large conversations."""
        headers = self.get_auth_headers(test_db, business_user)

        # Setup
        client_response = client.post(
            "/api/clients", headers=headers, json=enterprise_client
        )
        client_id = client_response.json()["id"]

        chatbot_data = {**complex_chatbot, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = chatbot_response.json()["id"]

        conv_data = {"chatbot_id": chatbot_id, "title": "Large Conversation Test"}
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conv_data
        )
        conversation_id = conv_response.json()["id"]

        # Add many messages
        start_time = time.time()
        for i in range(100):
            message_data = {
                "content": f"Test message number {i+1} with some content to make it realistic",
                "role": "user" if i % 2 == 0 else "assistant",
            }
            response = client.post(
                f"/api/conversations/{conversation_id}/messages",
                headers=headers,
                json=message_data,
            )
            assert response.status_code == 201

        end_time = time.time()
        total_time = end_time - start_time

        # Performance assertion - should complete within reasonable time
        assert total_time < 30.0  # 30 seconds for 100 messages

        # Verify retrieval performance
        start_time = time.time()
        messages_response = client.get(
            f"/api/conversations/{conversation_id}/messages", headers=headers
        )
        end_time = time.time()
        retrieval_time = end_time - start_time

        assert messages_response.status_code == 200
        assert len(messages_response.json()["messages"]) == 100
        assert retrieval_time < 5.0  # Should retrieve quickly

    def test_bulk_operations_performance(self, test_db, business_user):
        """Test performance of bulk operations."""
        headers = self.get_auth_headers(test_db, business_user)

        # Create multiple clients in bulk
        start_time = time.time()
        client_ids = []

        for i in range(50):
            client_data = {
                "name": f"Bulk Client {i+1}",
                "email": f"bulk{i+1}@example.com",
                "industry": "Technology",
            }
            response = client.post("/api/clients", headers=headers, json=client_data)
            assert response.status_code == 201
            client_ids.append(response.json()["id"])

        end_time = time.time()
        creation_time = end_time - start_time

        # Performance assertion
        assert creation_time < 60.0  # Should complete within 1 minute

        # Test bulk retrieval
        start_time = time.time()
        clients_response = client.get(
            "/api/clients", headers=headers, params={"limit": 100}
        )
        end_time = time.time()
        retrieval_time = end_time - start_time

        assert clients_response.status_code == 200
        assert len(clients_response.json()["clients"]) >= 50
        assert retrieval_time < 5.0  # Should retrieve quickly


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])
