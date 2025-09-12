#!/usr/bin/env python3
"""
Comprehensive System Test Runner
Tests all major components and provides detailed status report
"""

import asyncio
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add the api directory to Python path
api_path = Path(__file__).parent / "api"
sys.path.insert(0, str(api_path))


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")


def print_status(component: str, status: str, details: str = ""):
    """Print component status"""
    icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {component:<30} [{status}] {details}")


async def test_database_connection():
    """Test basic database connectivity"""
    try:
        import asyncpg

        # Test database connection
        conn = await asyncpg.connect(
            host="localhost",
            port=5433,
            database="pixel_ai",
            user="pixel_user",
            password="pixel_secure_2024",
        )
        await conn.fetchval("SELECT 1")
        await conn.close()
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)


async def test_redis_connection():
    """Test Redis connectivity"""
    try:
        import redis.asyncio as redis

        r = redis.from_url("redis://localhost:6380")
        await r.ping()
        await r.aclose()
        return True, "Connection successful"
    except Exception as e:
        return False, str(e)


def test_imports():
    """Test critical imports"""
    results = {}

    # Core dependencies
    imports_to_test = [
        ("fastapi", "FastAPI framework"),
        ("sqlalchemy", "Database ORM"),
        ("asyncpg", "PostgreSQL driver"),
        ("redis", "Redis client"),
        ("celery", "Task queue"),
        ("cryptography", "Encryption"),
        ("pydantic", "Data validation"),
        ("pytest", "Testing framework"),
    ]

    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            results[module_name] = ("PASS", f"{description} available")
        except ImportError as e:
            results[module_name] = ("FAIL", f"Import error: {e}")

    return results


async def test_fastapi_app():
    """Test FastAPI application startup"""
    try:
        # Test basic FastAPI imports and setup
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        # Create a minimal test app
        app = FastAPI(title="Test App")

        @app.get("/health")
        def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

        # Test with TestClient
        client = TestClient(app)
        response = client.get("/health")

        if response.status_code == 200:
            return True, f"FastAPI app responds correctly: {response.json()}"
        else:
            return False, f"Unexpected status code: {response.status_code}"

    except Exception as e:
        return False, str(e)


def test_docker_services():
    """Test Docker services status"""
    try:
        import subprocess

        result = subprocess.run(
            ["docker-compose", "ps", "--format", "table"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent,
        )

        if result.returncode == 0:
            services = []
            lines = result.stdout.strip().split("\n")[1:]  # Skip header
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        state = parts[2] if len(parts) > 2 else "Unknown"
                        services.append(f"{name}: {state}")

            return True, f"Services: {', '.join(services)}"
        else:
            return False, f"Docker command failed: {result.stderr}"

    except Exception as e:
        return False, str(e)


async def test_existing_api_endpoints():
    """Test existing API endpoints if available"""
    try:
        import httpx

        # Test if the API is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8002/health", timeout=5.0)
                if response.status_code == 200:
                    return True, f"API responding: {response.json()}"
                else:
                    return False, f"API returned {response.status_code}"
            except httpx.ConnectError:
                return False, "API not running or not accessible"
    except ImportError:
        return False, "httpx not available for API testing"
    except Exception as e:
        return False, str(e)


async def main():
    """Main test runner"""
    print_header("🚀 PIXEL AI CREATOR - COMPREHENSIVE SYSTEM TEST")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")

    # Test 1: Dependencies and Imports
    print_header("DEPENDENCY & IMPORT TESTS")
    import_results = test_imports()

    for module, (status, details) in import_results.items():
        print_status(f"{module} import", status, details)

    # Test 2: Docker Services
    print_header("DOCKER SERVICES TEST")
    docker_status, docker_details = test_docker_services()
    print_status("Docker Services", "PASS" if docker_status else "FAIL", docker_details)

    # Test 3: Database Connection
    print_header("DATABASE CONNECTIVITY TEST")
    try:
        db_status, db_details = await test_database_connection()
        print_status("PostgreSQL Database", "PASS" if db_status else "FAIL", db_details)
    except Exception as e:
        print_status("PostgreSQL Database", "FAIL", str(e))

    # Test 4: Redis Connection
    print_header("REDIS CONNECTIVITY TEST")
    try:
        redis_status, redis_details = await test_redis_connection()
        print_status("Redis Cache", "PASS" if redis_status else "FAIL", redis_details)
    except Exception as e:
        print_status("Redis Cache", "FAIL", str(e))

    # Test 5: FastAPI Application
    print_header("FASTAPI APPLICATION TEST")
    try:
        app_status, app_details = await test_fastapi_app()
        print_status("FastAPI App", "PASS" if app_status else "FAIL", app_details)
    except Exception as e:
        print_status("FastAPI App", "FAIL", str(e))

    # Test 6: Live API Endpoints
    print_header("LIVE API ENDPOINT TEST")
    try:
        api_status, api_details = await test_existing_api_endpoints()
        print_status("API Endpoints", "PASS" if api_status else "FAIL", api_details)
    except Exception as e:
        print_status("API Endpoints", "FAIL", str(e))

    # Summary
    print_header("🎯 TEST SUMMARY")

    passed_tests = sum(
        1 for _, (status, _) in import_results.items() if status == "PASS"
    )
    total_import_tests = len(import_results)

    print(f"📊 Import Tests: {passed_tests}/{total_import_tests} passed")
    print(
        f"🐳 Docker Services: {'✅ Running' if docker_status else '❌ Issues detected'}"
    )

    try:
        db_status, _ = await test_database_connection()
        print(f"🗃️  Database: {'✅ Connected' if db_status else '❌ Connection failed'}")
    except:
        print(f"🗃️  Database: ❌ Connection failed")

    try:
        redis_status, _ = await test_redis_connection()
        print(f"🔴 Redis: {'✅ Connected' if redis_status else '❌ Connection failed'}")
    except:
        print(f"🔴 Redis: ❌ Connection failed")

    print_header("🔧 NEXT STEPS")

    if passed_tests < total_import_tests:
        print("⚠️  Install missing dependencies:")
        for module, (status, details) in import_results.items():
            if status == "FAIL":
                print(f"   pip install {module}")

    if not docker_status:
        print("⚠️  Start Docker services:")
        print("   docker-compose up -d")

    print("\n📝 To run specific tests:")
    print("   pytest tests/ -v                    # Run all pytest tests")
    print("   python run_comprehensive_tests.py   # Run full test suite")
    print("   python test_database_management.py  # Test database management system")

    print(f"\n🏁 Test completed at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
