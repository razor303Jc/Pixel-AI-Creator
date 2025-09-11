"""
Simple async test to verify pytest configuration
"""

import pytest
import asyncio


@pytest.mark.asyncio
async def test_async_simple():
    """Test basic async functionality"""
    await asyncio.sleep(0.1)
    assert True


@pytest.mark.asyncio
async def test_async_with_fixture(mock_database):
    """Test with mocked database fixture"""
    # Mock database should be available from conftest.py
    assert mock_database is not None
    result = await mock_database.execute("SELECT 1")
    assert result is not None


def test_sync_simple():
    """Test basic sync functionality"""
    assert 1 + 1 == 2
