"""
Pytest configuration and fixtures for Pixel AI Creator tests
"""

import pytest
import pytest_asyncio
from unittest.mock import Mock
import asyncio
import sys
import os

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockDatabase:
    """Mock database for testing"""

    async def execute(self, query, *args):
        """Mock database execute method"""
        if "SELECT 1" in query:
            return [(1,)]
        return []

    async def fetch_one(self, query, *args):
        """Mock fetch one method"""
        return {"id": 1, "name": "test"}

    async def fetch_all(self, query, *args):
        """Mock fetch all method"""
        return [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]


class MockRedis:
    """Mock Redis for testing"""

    def __init__(self):
        self._data = {}

    async def get(self, key):
        """Mock Redis get"""
        return self._data.get(key)

    async def set(self, key, value, ex=None):
        """Mock Redis set"""
        self._data[key] = value
        return True

    async def delete(self, key):
        """Mock Redis delete"""
        if key in self._data:
            del self._data[key]
            return 1
        return 0


class MockOpenAI:
    """Mock OpenAI API for testing"""

    def __init__(self):
        self.chat = MockChatCompletions()


class MockChatCompletions:
    """Mock OpenAI chat completions"""

    async def create(self, **kwargs):
        """Mock chat completion creation"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Mock AI response"
        return mock_response


@pytest.fixture
def client():
    """Provide a test HTTP client for the FastAPI app"""
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)


@pytest_asyncio.fixture
async def mock_database():
    """Provide a mock database for testing"""
    return MockDatabase()


@pytest_asyncio.fixture
async def mock_redis():
    """Provide a mock Redis client for testing"""
    return MockRedis()


@pytest.fixture
def mock_openai():
    """Provide a mock OpenAI client for testing"""
    return MockOpenAI()


@pytest.fixture
def mock_settings():
    """Provide mock settings for testing"""
    return {
        "database_url": "sqlite+aiosqlite:///test.db",
        "redis_url": "redis://localhost:6379",
        "openai_api_key": "test_key",
        "secret_key": "test_secret",
        "environment": "testing",
    }


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Configure pytest for async testing
pytest_plugins = ("pytest_asyncio",)
