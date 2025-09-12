#!/usr/bin/env python3
"""
Quick Database Test
"""

import sys
from pathlib import Path

# Add the api directory to Python path
api_path = Path(__file__).parent / "api"
sys.path.insert(0, str(api_path))


def test_imports():
    print("Testing imports...")

    # Test 1: DatabaseConnectionManager
    try:
        from core.database_manager import DatabaseConnectionManager

        print("✅ DatabaseConnectionManager - OK")
    except Exception as e:
        print(f"❌ DatabaseConnectionManager - {e}")

    # Test 2: DatabaseMonitor
    try:
        from services.database_monitor import DatabaseMonitor

        print("✅ DatabaseMonitor - OK")
    except Exception as e:
        print(f"❌ DatabaseMonitor - {e}")

    # Test 3: DatabaseBackupService
    try:
        from services.database_backup import DatabaseBackupService

        print("✅ DatabaseBackupService - OK")
    except Exception as e:
        print(f"❌ DatabaseBackupService - {e}")

    # Test 4: DatabaseRoutes
    try:
        from routes.database_simple import router

        print("✅ DatabaseRoutes (simple) - OK")
    except Exception as e:
        print(f"❌ DatabaseRoutes (simple) - {e}")

    # Test 5: DatabaseMiddleware
    try:
        from middleware.database_middleware import DatabaseMiddleware

        print("✅ DatabaseMiddleware - OK")
    except Exception as e:
        print(f"❌ DatabaseMiddleware - {e}")


if __name__ == "__main__":
    test_imports()
    print("Import test completed!")
