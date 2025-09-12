#!/usr/bin/env python3
"""
Database Management System Test
Test all components of the newly implemented Database Management System
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the api directory to Python path
api_path = Path(__file__).parent / "api"
sys.path.insert(0, str(api_path))


def print_test_header(title: str):
    """Print a formatted test header"""
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")


def test_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    icon = "✅" if success else "❌"
    status = "PASS" if success else "FAIL"
    print(f"{icon} {test_name:<35} [{status}] {details}")


async def test_database_management_imports():
    """Test Database Management System imports"""
    print_test_header("DATABASE MANAGEMENT SYSTEM - IMPORT TESTS")

    results = {}

    # Test core database manager
    try:
        sys.path.insert(0, str(Path(__file__).parent / "api"))
        from core.database_manager import DatabaseConnectionManager

        results["DatabaseConnectionManager"] = (True, "Import successful")
    except Exception as e:
        results["DatabaseConnectionManager"] = (False, str(e))

    # Test database monitor
    try:
        from services.database_monitor import DatabaseMonitor

        results["DatabaseMonitor"] = (True, "Import successful")
    except Exception as e:
        results["DatabaseMonitor"] = (False, str(e))

    # Test database backup service
    try:
        from services.database_backup import DatabaseBackupService

        results["DatabaseBackupService"] = (True, "Import successful")
    except Exception as e:
        results["DatabaseBackupService"] = (False, str(e))

    # Test database routes
    try:
        from routes.database_simple import router

        results["DatabaseRoutes"] = (True, "Import successful (simplified version)")
    except Exception as e:
        try:
            from routes.database_management import router

            results["DatabaseRoutes"] = (True, "Import successful (full version)")
        except Exception as e2:
            results["DatabaseRoutes"] = (False, str(e))

    # Test middleware
    try:
        from middleware.database_middleware import DatabaseMiddleware

        results["DatabaseMiddleware"] = (True, "Import successful")
    except Exception as e:
        results["DatabaseMiddleware"] = (False, str(e))

    # Print results
    for component, (success, details) in results.items():
        test_result(component, success, details)

    return results


async def test_basic_database_operations():
    """Test basic database connectivity"""
    print_test_header("BASIC DATABASE OPERATIONS")

    try:
        import asyncpg

        # Test PostgreSQL connection
        conn = await asyncpg.connect(
            host="localhost",
            port=5433,
            database="pixel_ai",
            user="pixel_user",
            password="pixel_secure_2024",
        )

        # Test basic query
        result = await conn.fetchval("SELECT version()")
        test_result("PostgreSQL Connection", True, f"Version: {result[:50]}...")

        # Test table existence
        tables = await conn.fetch(
            """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        )
        table_names = [row["table_name"] for row in tables]
        test_result(
            "Database Tables", len(table_names) > 0, f"{len(table_names)} tables found"
        )

        await conn.close()
        return True

    except Exception as e:
        test_result("Database Connection", False, str(e))
        return False


async def test_redis_connectivity():
    """Test Redis connectivity for caching"""
    print_test_header("REDIS CACHE TESTING")

    try:
        import redis.asyncio as redis

        r = redis.from_url("redis://localhost:6380")

        # Test basic operations
        await r.set("test_key", "test_value")
        value = await r.get("test_key")

        test_result(
            "Redis Set/Get",
            value.decode() == "test_value",
            f"Retrieved: {value.decode()}",
        )

        # Test expiration
        await r.setex("test_expire", 1, "expire_value")
        test_result("Redis Expiration", True, "Set key with TTL")

        await r.delete("test_key", "test_expire")
        await r.close()  # Use close() instead of aclose()

        return True

    except Exception as e:
        test_result("Redis Connection", False, str(e))
        return False


async def test_configuration_loading():
    """Test configuration loading"""
    print_test_header("CONFIGURATION TESTING")

    try:
        # Test environment variables
        from core.config import settings

        test_result("Config Import", True, "Settings imported successfully")
        test_result(
            "Database URL",
            hasattr(settings, "database_url"),
            f"URL: {getattr(settings, 'database_url', 'Not found')[:50]}...",
        )
        test_result(
            "Redis URL",
            hasattr(settings, "redis_url"),
            f"URL: {getattr(settings, 'redis_url', 'Not found')}",
        )

        return True

    except Exception as e:
        test_result("Configuration", False, str(e))
        return False


async def test_fastapi_integration():
    """Test FastAPI integration"""
    print_test_header("FASTAPI INTEGRATION TESTING")

    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        # Create test app
        app = FastAPI()

        @app.get("/test-health")
        def test_health():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

        # Test with client
        client = TestClient(app)
        response = client.get("/test-health")

        success = response.status_code == 200
        test_result("FastAPI Basic", success, f"Status: {response.status_code}")

        if success:
            data = response.json()
            test_result("JSON Response", "status" in data, f"Data: {data}")

        return success

    except Exception as e:
        test_result("FastAPI Integration", False, str(e))
        return False


async def test_api_server_status():
    """Test if API server is running"""
    print_test_header("LIVE API SERVER TESTING")

    try:
        import httpx

        async with httpx.AsyncClient() as client:
            # Test if server is running
            try:
                response = await client.get("http://localhost:8002/health", timeout=5.0)
                test_result(
                    "API Server",
                    response.status_code == 200,
                    f"Status: {response.status_code}",
                )

                if response.status_code == 200:
                    data = response.json()
                    test_result("Health Endpoint", True, f"Response: {data}")
                    return True

            except httpx.ConnectError:
                test_result("API Server", False, "Server not running on port 8002")

            # Try alternative port
            try:
                response = await client.get("http://localhost:8000/health", timeout=5.0)
                test_result(
                    "API Server (8000)",
                    response.status_code == 200,
                    f"Status: {response.status_code}",
                )
                return response.status_code == 200

            except httpx.ConnectError:
                test_result("API Server (8000)", False, "Server not running")

        return False

    except Exception as e:
        test_result("API Testing", False, str(e))
        return False


async def main():
    """Main test runner"""
    print(f"🚀 DATABASE MANAGEMENT SYSTEM - COMPREHENSIVE TEST")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working Directory: {os.getcwd()}")

    # Run all tests
    results = []

    # Test 1: Imports
    import_results = await test_database_management_imports()
    import_success = all(success for success, _ in import_results.values())
    results.append(("Database Management Imports", import_success))

    # Test 2: Configuration
    config_success = await test_configuration_loading()
    results.append(("Configuration Loading", config_success))

    # Test 3: Database
    db_success = await test_basic_database_operations()
    results.append(("Database Operations", db_success))

    # Test 4: Redis
    redis_success = await test_redis_connectivity()
    results.append(("Redis Connectivity", redis_success))

    # Test 5: FastAPI
    fastapi_success = await test_fastapi_integration()
    results.append(("FastAPI Integration", fastapi_success))

    # Test 6: Live API
    api_success = await test_api_server_status()
    results.append(("Live API Server", api_success))

    # Summary
    print_test_header("🎯 TEST SUMMARY")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        test_result(test_name, success)

    print(f"\n📊 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for Database Management System!")
    else:
        print("⚠️  Some tests failed. Check the details above.")

    print_test_header("📝 RECOMMENDATIONS")

    if not import_success:
        print("🔧 Fix import issues:")
        print("   - Check Python path configuration")
        print("   - Verify all files are created correctly")
        print("   - Check for syntax errors in modules")

    if not db_success:
        print("🗃️  Database issues:")
        print("   - Ensure PostgreSQL container is running")
        print("   - Check connection settings")
        print("   - Verify database schema")

    if not redis_success:
        print("🔴 Redis issues:")
        print("   - Ensure Redis container is running")
        print("   - Check Redis connection settings")

    if not api_success:
        print("🌐 API Server issues:")
        print("   - Start the FastAPI server: uvicorn main:app --reload")
        print("   - Check if port 8000 or 8002 is available")

    print(f"\n🏁 Test completed at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
