#!/usr/bin/env python3
"""
FastAPI App Startup Debug Script
Isolates the FastAPI app startup issue for testing
"""

import asyncio
import sys
import os
import time
from pathlib import Path

# Add api directory to Python path
api_dir = Path(__file__).parent / "api"
sys.path.insert(0, str(api_dir))

async def test_database_connection():
    """Test database connection without FastAPI"""
    print("🔍 Testing Database Connection...")
    try:
        from api.core.database import test_connection
        result = await test_connection()
        if result:
            print("✅ Database connection successful")
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

async def test_database_init():
    """Test database initialization"""
    print("🔍 Testing Database Initialization...")
    try:
        from api.core.database import init_db
        await init_db()
        print("✅ Database initialization successful")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

async def test_fastapi_creation():
    """Test FastAPI app creation without startup events"""
    print("🔍 Testing FastAPI App Creation...")
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        
        # Create minimal app
        test_app = FastAPI(title="Test App")
        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @test_app.get("/health")
        async def health():
            return {"status": "healthy"}
            
        print("✅ FastAPI app creation successful")
        return True, test_app
    except Exception as e:
        print(f"❌ FastAPI app creation error: {e}")
        return False, None

async def test_imports():
    """Test all critical imports"""
    print("🔍 Testing Critical Imports...")
    imports_to_test = [
        ("api.core.config", "settings"),
        ("api.core.database", "init_db"),
        ("api.routes.embeddings", "router"),
        ("api.routes.clients", "router"), 
        ("api.routes.chatbots", "router"),
        ("api.routes.conversations", "router"),
        ("api.auth.routes", "router"),
    ]
    
    failed_imports = []
    for module_name, attr_name in imports_to_test:
        try:
            module = __import__(module_name, fromlist=[attr_name])
            getattr(module, attr_name)
            print(f"✅ {module_name}.{attr_name}")
        except Exception as e:
            print(f"❌ {module_name}.{attr_name}: {e}")
            failed_imports.append((module_name, attr_name, str(e)))
    
    return len(failed_imports) == 0, failed_imports

def test_environment():
    """Test environment configuration"""
    print("🔍 Testing Environment Configuration...")
    
    # Check .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")
    
    # Check critical env vars
    critical_vars = ["DATABASE_URL", "SECRET_KEY"]
    missing_vars = []
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is missing")
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars

async def main():
    """Run comprehensive FastAPI startup debugging"""
    print("🚀 FastAPI Startup Debug Suite")
    print("=" * 50)
    
    # Test 1: Environment
    env_ok, missing_vars = test_environment()
    if not env_ok:
        print(f"🚨 Environment issues: Missing {missing_vars}")
        return
    
    # Test 2: Imports
    imports_ok, failed_imports = await test_imports()
    if not imports_ok:
        print(f"🚨 Import issues:")
        for module, attr, error in failed_imports:
            print(f"   - {module}.{attr}: {error}")
        return
    
    # Test 3: Database Connection
    db_conn_ok = await test_database_connection()
    if not db_conn_ok:
        print("🚨 Database connection issues")
        # Continue anyway to test other components
    
    # Test 4: Database Initialization
    if db_conn_ok:
        db_init_ok = await test_database_init()
        if not db_init_ok:
            print("🚨 Database initialization issues")
    
    # Test 5: FastAPI App Creation
    app_ok, test_app = await test_fastapi_creation()
    if not app_ok:
        print("🚨 FastAPI app creation issues")
        return
    
    # Test 6: Minimal HTTP Test
    print("🔍 Testing Minimal HTTP Server...")
    try:
        import uvicorn
        from fastapi.testclient import TestClient
        
        client = TestClient(test_app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ Minimal HTTP server test successful")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ HTTP test failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ HTTP test error: {e}")
    
    print("\n🏁 Debug Complete")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
