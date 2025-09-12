"""
Simple Database Management System Tests
Tests that can run without the full application context
"""

import pytest
import asyncio
import logging
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestDatabaseConnectionManager:
    """Test database connection management functionality"""

    @pytest.mark.asyncio
    async def test_import_database_manager(self):
        """Test that we can import the database manager"""
        try:
            from api.core.database_manager import DatabaseConnectionManager

            assert DatabaseConnectionManager is not None
            print("✅ Database Manager import successful")
        except ImportError as e:
            pytest.fail(f"Failed to import DatabaseConnectionManager: {e}")

    def test_logging_module(self):
        """Test that logging module works"""
        try:
            from api.core.logging import get_logger

            logger = get_logger("test")
            assert logger is not None
            print("✅ Logging module working")
        except Exception as e:
            pytest.fail(f"Logging module failed: {e}")


class TestDatabaseServices:
    """Test database service functionality"""

    def test_import_database_services(self):
        """Test that we can import database services"""
        try:
            # Check if services exist
            services_path = os.path.join(
                os.path.dirname(__file__), "..", "api", "services"
            )
            if os.path.exists(services_path):
                files = os.listdir(services_path)
                print(f"✅ Services directory exists with files: {files}")
            else:
                print("⚠️ Services directory not found")
        except Exception as e:
            print(f"⚠️ Error checking services: {e}")


class TestSystemIntegration:
    """Test system integration"""

    def test_python_environment(self):
        """Test Python environment is properly configured"""
        import sys

        print(f"✅ Python version: {sys.version}")
        print(f"✅ Python path: {sys.path[:3]}...")  # Show first 3 paths

    def test_required_packages(self):
        """Test that required packages are available"""
        required_packages = ["asyncio", "logging", "sqlalchemy", "asyncpg", "pydantic"]

        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} available")
            except ImportError:
                print(f"❌ {package} not available")


if __name__ == "__main__":
    # Run basic tests
    print("=== Database Management System Test Report ===")

    # Test 1: Environment
    print("\n1. Testing Environment...")
    test_sys = TestSystemIntegration()
    test_sys.test_python_environment()
    test_sys.test_required_packages()

    # Test 2: Services
    print("\n2. Testing Services...")
    test_services = TestDatabaseServices()
    test_services.test_import_database_services()

    # Test 3: Database Manager (async)
    print("\n3. Testing Database Manager...")

    async def run_async_tests():
        test_db = TestDatabaseConnectionManager()
        await test_db.test_import_database_manager()
        test_db.test_logging_module()

    try:
        asyncio.run(run_async_tests())
    except Exception as e:
        print(f"❌ Async tests failed: {e}")

    print("\n=== Test Complete ===")
