import pytest
import asyncio
import json
import os
import httpx
from httpx import AsyncClient
from typing import Dict, Any

from main import app
from core.database import Base

# Test configuration - use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Set test environment variables
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_URL"] = "redis://localhost:6380"
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def setup_test_db():
    """Setup test database with mocked dependencies"""
    # Create test database tables
    from sqlalchemy.ext.asyncio import create_async_engine

    test_engine = create_async_engine(TEST_DATABASE_URL)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    # Cleanup
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def client(setup_test_db):
    """Create test client"""
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


@pytest.fixture
async def test_client_data():
    """Sample client data for testing"""
    return {
        "name": "Test Restaurant",
        "email": "test@restaurant.com",
        "company": "Pizza Palace",
        "website": "https://pizzapalace.com",
        "phone": "+1-555-0123",
        "industry": "Food & Beverage",
        "description": "A local pizzeria specializing in authentic Italian pizza",
        "twitter_handle": "pizzapalace",
        "instagram_handle": "pizzapalace_official",
        "linkedin_profile": "pizza-palace-restaurant",
    }


class TestHealthChecks:
    """Test basic health and connectivity"""

    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns welcome message"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "Pixel AI Creator" in data["message"]

    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_pixel_status(self, client: AsyncClient):
        """Test Pixel AI status endpoint"""
        response = await client.get("/api/pixel/status")
        assert response.status_code == 200
        data = response.json()
        assert data["pixel_status"] == "online"
        assert "capabilities" in data
        assert isinstance(data["capabilities"], list)


class TestClientManagement:
    """Test client CRUD operations"""

    async def test_create_client(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test creating a new client"""
        response = await client.post("/api/clients", json=test_client_data)
        assert response.status_code == 200

        data = response.json()
        assert data["name"] == test_client_data["name"]
        assert data["email"] == test_client_data["email"]
        assert data["company"] == test_client_data["company"]
        assert "id" in data
        assert "created_at" in data

        return data["id"]  # Return client ID for other tests

    async def test_create_duplicate_client(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test creating client with duplicate email fails"""
        # Create first client
        await client.post("/api/clients", json=test_client_data)

        # Try to create duplicate
        response = await client.post("/api/clients", json=test_client_data)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    async def test_get_clients(self, client: AsyncClient):
        """Test getting all clients"""
        response = await client.get("/api/clients")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    async def test_get_client_by_id(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test getting client by ID"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Get client by ID
        response = await client.get(f"/api/clients/{client_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == client_id
        assert data["name"] == test_client_data["name"]

    async def test_get_nonexistent_client(self, client: AsyncClient):
        """Test getting non-existent client returns 404"""
        response = await client.get("/api/clients/99999")
        assert response.status_code == 404


class TestWebAnalysis:
    """Test web analysis functionality"""

    async def test_analyze_website(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test website analysis endpoint"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Start website analysis
        response = await client.post(
            "/api/analyze/website",
            params={"url": test_client_data["website"], "client_id": client_id},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["url"] == test_client_data["website"]
        assert data["client_id"] == client_id

    async def test_analyze_social_media(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test social media analysis endpoint"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Start social media analysis
        response = await client.post(
            "/api/analyze/social-media",
            params={
                "platform": "twitter",
                "handle": test_client_data["twitter_handle"],
                "client_id": client_id,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "processing"
        assert data["platform"] == "twitter"
        assert data["handle"] == test_client_data["twitter_handle"]


class TestProjectManagement:
    """Test project CRUD operations"""

    async def test_create_project(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test creating a new project"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Create project
        project_data = {
            "client_id": client_id,
            "name": "Pizza Chatbot",
            "description": "AI assistant for pizza ordering",
            "assistant_type": "chatbot",
            "complexity": "basic",
        }

        response = await client.post("/api/projects", json=project_data)
        assert response.status_code == 200

        data = response.json()
        assert data["client_id"] == client_id
        assert data["name"] == project_data["name"]
        assert data["status"] == "pending"
        assert data["progress"] == 0

    async def test_get_client_projects(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test getting projects for a client"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Get projects (should be empty initially)
        response = await client.get(f"/api/projects/{client_id}")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)


class TestQASessions:
    """Test Q&A session functionality"""

    async def test_create_qa_session(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test creating Q&A session"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Create Q&A session
        response = await client.post("/api/qa/session", params={"client_id": client_id})

        assert response.status_code == 200
        data = response.json()
        assert data["client_id"] == client_id
        assert data["status"] == "active"
        assert "id" in data

        return data["id"]  # Return session ID

    async def test_record_qa(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test recording Q&A pairs"""
        # Create client and session
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        session_response = await client.post(
            "/api/qa/session", params={"client_id": client_id}
        )
        session_id = session_response.json()["id"]

        # Record Q&A
        response = await client.post(
            "/api/qa/question",
            params={
                "session_id": session_id,
                "question": "What are your business hours?",
                "answer": "We're open Monday-Sunday 11AM-10PM",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "Q&A recorded" in data["message"]
        assert data["total_pairs"] == 1


class TestAIGeneration:
    """Test AI assistant generation"""

    async def test_generate_assistant(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test AI assistant generation endpoint"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Start AI generation
        response = await client.post(
            "/api/generate/assistant",
            params={
                "client_id": client_id,
                "assistant_type": "chatbot",
                "complexity": "basic",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "generating"
        assert data["client_id"] == client_id
        assert data["type"] == "chatbot"


class TestInputValidation:
    """Test input validation and error handling"""

    async def test_invalid_email_format(self, client: AsyncClient):
        """Test invalid email format is rejected"""
        invalid_data = {
            "name": "Test Client",
            "email": "invalid-email",  # Invalid format
            "company": "Test Company",
        }

        response = await client.post("/api/clients", json=invalid_data)
        assert response.status_code == 422  # Validation error

    async def test_missing_required_fields(self, client: AsyncClient):
        """Test missing required fields are rejected"""
        incomplete_data = {
            "name": "Test Client"
            # Missing email
        }

        response = await client.post("/api/clients", json=incomplete_data)
        assert response.status_code == 422  # Validation error

    async def test_invalid_project_data(self, client: AsyncClient):
        """Test invalid project data is rejected"""
        invalid_project = {
            "client_id": 99999,  # Non-existent client
            "name": "Test Project",
        }

        response = await client.post("/api/projects", json=invalid_project)
        assert response.status_code == 400


class TestConcurrency:
    """Test concurrent operations"""

    async def test_concurrent_client_creation(self, client: AsyncClient):
        """Test multiple clients can be created concurrently"""
        tasks = []

        for i in range(5):
            client_data = {
                "name": f"Test Client {i}",
                "email": f"test{i}@example.com",
                "company": f"Company {i}",
            }
            task = client.post("/api/clients", json=client_data)
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200

    async def test_concurrent_analysis_requests(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test multiple analysis requests can be handled concurrently"""
        # Create client first
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Start multiple analyses concurrently
        tasks = [
            client.post(
                "/api/analyze/website",
                params={"url": test_client_data["website"], "client_id": client_id},
            ),
            client.post(
                "/api/analyze/social-media",
                params={
                    "platform": "twitter",
                    "handle": test_client_data["twitter_handle"],
                    "client_id": client_id,
                },
            ),
        ]

        responses = await asyncio.gather(*tasks)

        # All should start successfully
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "processing"


class TestDataIntegrity:
    """Test data integrity and consistency"""

    async def test_client_project_relationship(
        self, client: AsyncClient, test_client_data: Dict[str, Any]
    ):
        """Test client-project relationship integrity"""
        # Create client
        create_response = await client.post("/api/clients", json=test_client_data)
        client_id = create_response.json()["id"]

        # Create project
        project_data = {
            "client_id": client_id,
            "name": "Test Project",
            "assistant_type": "chatbot",
            "complexity": "basic",
        }

        project_response = await client.post("/api/projects", json=project_data)
        assert project_response.status_code == 200

        # Verify project appears in client's projects
        projects_response = await client.get(f"/api/projects/{client_id}")
        projects = projects_response.json()

        assert len(projects) == 1
        assert projects[0]["name"] == project_data["name"]


# Performance and load testing
class TestPerformance:
    """Test system performance under load"""

    @pytest.mark.slow
    async def test_bulk_client_operations(self, client: AsyncClient):
        """Test creating many clients (performance test)"""
        start_time = asyncio.get_event_loop().time()

        tasks = []
        for i in range(100):
            client_data = {
                "name": f"Bulk Client {i}",
                "email": f"bulk{i}@example.com",
                "company": f"Bulk Company {i}",
            }
            tasks.append(client.post("/api/clients", json=client_data))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Check that most requests succeeded
        successful = sum(
            1 for r in responses if hasattr(r, "status_code") and r.status_code == 200
        )
        assert successful >= 95  # At least 95% success rate

        # Performance check - should handle 100 requests reasonably fast
        assert duration < 30  # Less than 30 seconds for 100 requests

        print(f"Created {successful}/100 clients in {duration:.2f}s")


# Integration tests
class TestIntegration:
    """Test complete workflows end-to-end"""

    async def test_complete_client_onboarding_workflow(self, client: AsyncClient):
        """Test complete client onboarding process"""
        # Step 1: Create client
        client_data = {
            "name": "Integration Test Restaurant",
            "email": "integration@test.com",
            "company": "Test Restaurant",
            "website": "https://test-restaurant.com",
            "industry": "Food & Beverage",
        }

        client_response = await client.post("/api/clients", json=client_data)
        assert client_response.status_code == 200
        client_id = client_response.json()["id"]

        # Step 2: Start website analysis
        analysis_response = await client.post(
            "/api/analyze/website",
            params={"url": client_data["website"], "client_id": client_id},
        )
        assert analysis_response.status_code == 200

        # Step 3: Create Q&A session
        qa_response = await client.post(
            "/api/qa/session", params={"client_id": client_id}
        )
        assert qa_response.status_code == 200
        session_id = qa_response.json()["id"]

        # Step 4: Record some Q&A
        await client.post(
            "/api/qa/question",
            params={
                "session_id": session_id,
                "question": "What are your specialties?",
                "answer": "We specialize in wood-fired pizza and fresh pasta",
            },
        )

        # Step 5: Create AI project
        project_response = await client.post(
            "/api/projects",
            json={
                "client_id": client_id,
                "name": "Restaurant Assistant",
                "assistant_type": "chatbot",
                "complexity": "basic",
            },
        )
        assert project_response.status_code == 200

        # Step 6: Start AI generation
        generation_response = await client.post(
            "/api/generate/assistant",
            params={
                "client_id": client_id,
                "assistant_type": "chatbot",
                "complexity": "basic",
            },
        )
        assert generation_response.status_code == 200

        print("✅ Complete client onboarding workflow tested successfully")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
