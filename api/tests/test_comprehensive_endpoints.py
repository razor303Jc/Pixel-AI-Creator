"""
Comprehensive API endpoint testing suite for Pixel AI Creator.

This test suite covers:
- All API endpoints with various scenarios
- Authentication and authorization testing
- Error handling and edge cases
- Performance and load testing
- Integration workflow testing
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from unittest.mock import Mock, patch
import json
from datetime import datetime, timedelta

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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
def test_user():
    """Create a test user."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "user",
    }


@pytest.fixture
def admin_user():
    """Create an admin test user."""
    return {
        "email": "admin@example.com",
        "password": "adminpassword123",
        "full_name": "Admin User",
        "role": "admin",
    }


@pytest.fixture
def test_client_data():
    """Create test client data."""
    return {
        "name": "Test Client Inc.",
        "email": "client@testcorp.com",
        "industry": "Technology",
        "description": "A test client for our test suite",
        "requirements": "Basic chatbot functionality",
    }


@pytest.fixture
def test_chatbot_data():
    """Create test chatbot data."""
    return {
        "name": "Test Bot",
        "type": "chatbot",
        "complexity": "basic",
        "requirements": "Customer support chatbot",
        "industry": "Technology",
        "personality": "Professional and helpful",
    }


class TestAuthentication:
    """Test suite for authentication endpoints."""

    def test_user_registration(self, test_db, test_user):
        """Test user registration endpoint."""
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["full_name"] == test_user["full_name"]
        assert "access_token" in data
        assert "token_type" in data

    def test_duplicate_email_registration(self, test_db, test_user):
        """Test that duplicate email registration fails."""
        # Register first user
        client.post("/api/auth/register", json=test_user)

        # Try to register again with same email
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_invalid_email_registration(self, test_db):
        """Test registration with invalid email."""
        invalid_user = {
            "email": "invalid-email",
            "password": "testpassword123",
            "full_name": "Test User",
        }
        response = client.post("/api/auth/register", json=invalid_user)
        assert response.status_code == 422

    def test_user_login(self, test_db, test_user):
        """Test user login endpoint."""
        # First register the user
        client.post("/api/auth/register", json=test_user)

        # Then login
        login_data = {"email": test_user["email"], "password": test_user["password"]}
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == test_user["email"]

    def test_invalid_login(self, test_db, test_user):
        """Test login with invalid credentials."""
        # Register user first
        client.post("/api/auth/register", json=test_user)

        # Try login with wrong password
        login_data = {"email": test_user["email"], "password": "wrongpassword"}
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, test_db):
        """Test login with non-existent user."""
        login_data = {"email": "nonexistent@example.com", "password": "password123"}
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401

    def test_get_current_user_profile(self, test_db, test_user):
        """Test getting current user profile."""
        # Register and login
        register_response = client.post("/api/auth/register", json=test_user)
        token = register_response.json()["access_token"]

        # Get profile
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["full_name"] == test_user["full_name"]

    def test_update_user_profile(self, test_db, test_user):
        """Test updating user profile."""
        # Register and login
        register_response = client.post("/api/auth/register", json=test_user)
        token = register_response.json()["access_token"]

        # Update profile
        headers = {"Authorization": f"Bearer {token}"}
        update_data = {"full_name": "Updated Test User"}
        response = client.put("/api/auth/profile", headers=headers, json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Test User"

    def test_change_password(self, test_db, test_user):
        """Test password change functionality."""
        # Register and login
        register_response = client.post("/api/auth/register", json=test_user)
        token = register_response.json()["access_token"]

        # Change password
        headers = {"Authorization": f"Bearer {token}"}
        password_data = {
            "current_password": test_user["password"],
            "new_password": "newpassword123",
        }
        response = client.post(
            "/api/auth/change-password", headers=headers, json=password_data
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password updated successfully"

    def test_unauthorized_access(self, test_db):
        """Test accessing protected endpoint without token."""
        response = client.get("/api/auth/profile")
        assert response.status_code == 401


class TestClientManagement:
    """Test suite for client management endpoints."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_client(self, test_db, test_user, test_client_data):
        """Test client creation."""
        headers = self.get_auth_headers(test_db, test_user)
        response = client.post("/api/clients", headers=headers, json=test_client_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_client_data["name"]
        assert data["email"] == test_client_data["email"]
        assert data["industry"] == test_client_data["industry"]

    def test_list_clients(self, test_db, test_user, test_client_data):
        """Test listing clients."""
        headers = self.get_auth_headers(test_db, test_user)

        # Create a client first
        client.post("/api/clients", headers=headers, json=test_client_data)

        # List clients
        response = client.get("/api/clients", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["clients"]) >= 1
        assert "pagination" in data

    def test_get_client_by_id(self, test_db, test_user, test_client_data):
        """Test getting specific client."""
        headers = self.get_auth_headers(test_db, test_user)

        # Create client
        create_response = client.post(
            "/api/clients", headers=headers, json=test_client_data
        )
        client_id = create_response.json()["id"]

        # Get client
        response = client.get(f"/api/clients/{client_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == client_id
        assert data["name"] == test_client_data["name"]

    def test_update_client(self, test_db, test_user, test_client_data):
        """Test updating client information."""
        headers = self.get_auth_headers(test_db, test_user)

        # Create client
        create_response = client.post(
            "/api/clients", headers=headers, json=test_client_data
        )
        client_id = create_response.json()["id"]

        # Update client
        update_data = {"name": "Updated Client Name"}
        response = client.put(
            f"/api/clients/{client_id}", headers=headers, json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Client Name"

    def test_delete_client(self, test_db, test_user, test_client_data):
        """Test client deletion."""
        headers = self.get_auth_headers(test_db, test_user)

        # Create client
        create_response = client.post(
            "/api/clients", headers=headers, json=test_client_data
        )
        client_id = create_response.json()["id"]

        # Delete client
        response = client.delete(f"/api/clients/{client_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "Client deleted successfully"

    def test_client_stats(self, test_db, test_user, test_client_data):
        """Test client statistics endpoint."""
        headers = self.get_auth_headers(test_db, test_user)

        # Create client first
        client.post("/api/clients", headers=headers, json=test_client_data)

        # Get stats
        response = client.get("/api/clients/stats/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_clients" in data
        assert "active_clients" in data


class TestChatbotManagement:
    """Test suite for chatbot management endpoints."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def create_test_client(self, headers, client_data):
        """Helper to create a test client."""
        response = client.post("/api/clients", headers=headers, json=client_data)
        return response.json()["id"]

    def test_create_chatbot(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test chatbot creation."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id = self.create_test_client(headers, test_client_data)

        chatbot_data = {**test_chatbot_data, "client_id": client_id}
        response = client.post("/api/chatbots", headers=headers, json=chatbot_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == test_chatbot_data["name"]
        assert data["type"] == test_chatbot_data["type"]
        assert data["client_id"] == client_id

    def test_list_chatbots(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test listing chatbots."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id = self.create_test_client(headers, test_client_data)

        # Create chatbot
        chatbot_data = {**test_chatbot_data, "client_id": client_id}
        client.post("/api/chatbots", headers=headers, json=chatbot_data)

        # List chatbots
        response = client.get("/api/chatbots", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["chatbots"]) >= 1

    def test_get_chatbot_by_id(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test getting specific chatbot."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id = self.create_test_client(headers, test_client_data)

        # Create chatbot
        chatbot_data = {**test_chatbot_data, "client_id": client_id}
        create_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = create_response.json()["id"]

        # Get chatbot
        response = client.get(f"/api/chatbots/{chatbot_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == chatbot_id
        assert data["name"] == test_chatbot_data["name"]

    def test_update_chatbot(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test updating chatbot."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id = self.create_test_client(headers, test_client_data)

        # Create chatbot
        chatbot_data = {**test_chatbot_data, "client_id": client_id}
        create_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = create_response.json()["id"]

        # Update chatbot
        update_data = {"name": "Updated Bot Name"}
        response = client.put(
            f"/api/chatbots/{chatbot_id}", headers=headers, json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Bot Name"

    def test_chatbot_status_update(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test chatbot status updates."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id = self.create_test_client(headers, test_client_data)

        # Create chatbot
        chatbot_data = {**test_chatbot_data, "client_id": client_id}
        create_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        chatbot_id = create_response.json()["id"]

        # Update status
        status_data = {"status": "analyzing", "progress": 50}
        response = client.patch(
            f"/api/chatbots/{chatbot_id}/status", headers=headers, json=status_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "analyzing"
        assert data["progress"] == 50


class TestConversationManagement:
    """Test suite for conversation management endpoints."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def create_test_setup(self, headers, client_data, chatbot_data):
        """Helper to create client and chatbot."""
        # Create client
        client_response = client.post("/api/clients", headers=headers, json=client_data)
        client_id = client_response.json()["id"]

        # Create chatbot
        chatbot_data_with_client = {**chatbot_data, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data_with_client
        )
        chatbot_id = chatbot_response.json()["id"]

        return client_id, chatbot_id

    def test_create_conversation(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test conversation creation."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id, chatbot_id = self.create_test_setup(
            headers, test_client_data, test_chatbot_data
        )

        conversation_data = {
            "chatbot_id": chatbot_id,
            "title": "Test Conversation",
            "initial_message": "Hello, I need help",
        }
        response = client.post(
            "/api/conversations", headers=headers, json=conversation_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["chatbot_id"] == chatbot_id

    def test_list_conversations(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test listing conversations."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id, chatbot_id = self.create_test_setup(
            headers, test_client_data, test_chatbot_data
        )

        # Create conversation
        conversation_data = {"chatbot_id": chatbot_id, "title": "Test Conversation"}
        client.post("/api/conversations", headers=headers, json=conversation_data)

        # List conversations
        response = client.get("/api/conversations", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["conversations"]) >= 1

    def test_add_message_to_conversation(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test adding messages to conversation."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id, chatbot_id = self.create_test_setup(
            headers, test_client_data, test_chatbot_data
        )

        # Create conversation
        conversation_data = {"chatbot_id": chatbot_id, "title": "Test Conversation"}
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conversation_data
        )
        conversation_id = conv_response.json()["id"]

        # Add message
        message_data = {"content": "Hello, this is a test message", "role": "user"}
        response = client.post(
            f"/api/conversations/{conversation_id}/messages",
            headers=headers,
            json=message_data,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["role"] == message_data["role"]

    def test_get_conversation_messages(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test retrieving conversation messages."""
        headers = self.get_auth_headers(test_db, test_user)
        client_id, chatbot_id = self.create_test_setup(
            headers, test_client_data, test_chatbot_data
        )

        # Create conversation and add message
        conversation_data = {"chatbot_id": chatbot_id, "title": "Test Conversation"}
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conversation_data
        )
        conversation_id = conv_response.json()["id"]

        message_data = {"content": "Test message", "role": "user"}
        client.post(
            f"/api/conversations/{conversation_id}/messages",
            headers=headers,
            json=message_data,
        )

        # Get messages
        response = client.get(
            f"/api/conversations/{conversation_id}/messages", headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) >= 1


class TestLanguageEndpoints:
    """Test suite for multi-language endpoints."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_supported_languages(self, test_db, test_user):
        """Test getting supported languages."""
        headers = self.get_auth_headers(test_db, test_user)
        response = client.get("/api/language/supported", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0

    def test_detect_language(self, test_db, test_user):
        """Test language detection."""
        headers = self.get_auth_headers(test_db, test_user)
        text_data = {"text": "Hello, how are you today?"}
        response = client.post("/api/language/detect", headers=headers, json=text_data)
        assert response.status_code == 200
        data = response.json()
        assert "detected_language" in data
        assert "confidence" in data

    def test_translate_text(self, test_db, test_user):
        """Test text translation."""
        headers = self.get_auth_headers(test_db, test_user)
        translation_data = {
            "text": "Hello world",
            "target_language": "es",
            "source_language": "en",
        }
        response = client.post(
            "/api/language/translate", headers=headers, json=translation_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert "source_language" in data
        assert "target_language" in data


class TestPerformanceEndpoints:
    """Test suite for performance monitoring endpoints."""

    def get_auth_headers(self, test_db, user_data):
        """Helper to get authentication headers."""
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    @patch("services.cache_service.CacheService")
    def test_get_cache_stats(self, mock_cache_service, test_db, test_user):
        """Test cache statistics endpoint."""
        headers = self.get_auth_headers(test_db, test_user)

        # Mock cache stats
        mock_cache_service.return_value.get_stats.return_value = {
            "hit_rate": 85.5,
            "total_keys": 150,
            "memory_usage": "2.5MB",
        }

        response = client.get("/api/performance/cache/stats", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "cache_stats" in data

    @patch("services.background_tasks.TaskManager")
    def test_get_active_tasks(self, mock_task_manager, test_db, test_user):
        """Test active tasks endpoint."""
        headers = self.get_auth_headers(test_db, test_user)

        # Mock active tasks
        mock_task_manager.get_active_tasks.return_value = [
            {
                "task_id": "test-task-123",
                "name": "test_task",
                "status": "running",
                "worker": "worker@hostname",
            }
        ]

        response = client.get("/api/performance/tasks/active", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "active_tasks" in data


class TestErrorHandling:
    """Test suite for error handling scenarios."""

    def test_404_not_found(self, test_db):
        """Test 404 error handling."""
        response = client.get("/api/nonexistent-endpoint")
        assert response.status_code == 404

    def test_invalid_json_request(self, test_db):
        """Test invalid JSON handling."""
        response = client.post(
            "/api/auth/register",
            data="invalid json",
            headers={"content-type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_fields(self, test_db):
        """Test missing required fields handling."""
        incomplete_user = {
            "email": "test@example.com"
            # Missing password and full_name
        }
        response = client.post("/api/auth/register", json=incomplete_user)
        assert response.status_code == 422

    def test_invalid_token_format(self, test_db):
        """Test invalid token format handling."""
        headers = {"Authorization": "Bearer invalid-token-format"}
        response = client.get("/api/auth/profile", headers=headers)
        assert response.status_code == 401


class TestLoadAndPerformance:
    """Test suite for load and performance testing."""

    def test_concurrent_user_registration(self, test_db):
        """Test concurrent user registrations."""
        import threading
        import time

        results = []

        def register_user(user_id):
            user_data = {
                "email": f"user{user_id}@example.com",
                "password": "password123",
                "full_name": f"User {user_id}",
            }
            response = client.post("/api/auth/register", json=user_data)
            results.append(response.status_code)

        # Create 10 concurrent registration requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_user, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all registrations were successful
        assert all(status == 201 for status in results)
        assert len(results) == 10

    def test_api_response_time(self, test_db, test_user):
        """Test API response times."""
        import time

        # Register user
        register_response = client.post("/api/auth/register", json=test_user)
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test response time for profile endpoint
        start_time = time.time()
        response = client.get("/api/auth/profile", headers=headers)
        end_time = time.time()

        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second


# Integration test for complete workflows
class TestIntegrationWorkflows:
    """Test suite for complete integration workflows."""

    def test_complete_client_workflow(
        self, test_db, test_user, test_client_data, test_chatbot_data
    ):
        """Test complete client workflow from registration to chatbot creation."""
        # 1. Register user
        register_response = client.post("/api/auth/register", json=test_user)
        assert register_response.status_code == 201
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create client
        client_response = client.post(
            "/api/clients", headers=headers, json=test_client_data
        )
        assert client_response.status_code == 201
        client_id = client_response.json()["id"]

        # 3. Create chatbot for client
        chatbot_data = {**test_chatbot_data, "client_id": client_id}
        chatbot_response = client.post(
            "/api/chatbots", headers=headers, json=chatbot_data
        )
        assert chatbot_response.status_code == 201
        chatbot_id = chatbot_response.json()["id"]

        # 4. Create conversation
        conversation_data = {
            "chatbot_id": chatbot_id,
            "title": "Integration Test Conversation",
        }
        conv_response = client.post(
            "/api/conversations", headers=headers, json=conversation_data
        )
        assert conv_response.status_code == 201
        conversation_id = conv_response.json()["id"]

        # 5. Add messages to conversation
        message_data = {"content": "Hello from integration test", "role": "user"}
        msg_response = client.post(
            f"/api/conversations/{conversation_id}/messages",
            headers=headers,
            json=message_data,
        )
        assert msg_response.status_code == 201

        # 6. Verify the complete workflow
        final_conversation = client.get(
            f"/api/conversations/{conversation_id}", headers=headers
        )
        assert final_conversation.status_code == 200
        assert final_conversation.json()["chatbot_id"] == chatbot_id

    def test_user_permission_workflow(
        self, test_db, test_user, admin_user, test_client_data
    ):
        """Test user permission and access control workflow."""
        # Register regular user and admin
        user_response = client.post("/api/auth/register", json=test_user)
        admin_response = client.post("/api/auth/register", json=admin_user)

        user_token = user_response.json()["access_token"]
        admin_token = admin_response.json()["access_token"]

        user_headers = {"Authorization": f"Bearer {user_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        # User creates a client
        client_response = client.post(
            "/api/clients", headers=user_headers, json=test_client_data
        )
        assert client_response.status_code == 201
        client_id = client_response.json()["id"]

        # User can access their own client
        get_response = client.get(f"/api/clients/{client_id}", headers=user_headers)
        assert get_response.status_code == 200

        # Admin can also access the client
        admin_get_response = client.get(
            f"/api/clients/{client_id}", headers=admin_headers
        )
        assert admin_get_response.status_code == 200


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
