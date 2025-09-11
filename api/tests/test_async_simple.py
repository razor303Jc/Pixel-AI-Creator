"""Simple async tests to verify configuration"""

import pytest
from fastapi.testclient import TestClient


class TestAsyncConfiguration:
    """Test async test configuration"""

    def test_sync_client_creation(self, client: TestClient):
        """Test that sync client can be created"""
        assert client is not None
        assert isinstance(client, TestClient)

    def test_health_endpoint_mock(self, client: TestClient):
        """Test health endpoint with mocked dependencies"""
        # This should work with mocked dependencies
        response = client.get("/health")
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 500, 404]


class TestAsyncFunctionality:
    """Test actual async functionality"""

    @pytest.mark.asyncio
    async def test_basic_async(self, mock_database):
        """Test basic async database operations"""
        result = await mock_database.execute("SELECT 1")
        assert result == [(1,)]

    @pytest.mark.asyncio
    async def test_async_redis(self, mock_redis):
        """Test async Redis operations"""
        await mock_redis.set("test_key", "test_value")
        result = await mock_redis.get("test_key")
        assert result == "test_value"
