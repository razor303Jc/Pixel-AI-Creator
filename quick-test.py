#!/usr/bin/env python3
"""
Quick API Test Runner - Tests core functionality

This script runs essential tests to validate our API implementation
without requiring complex test setup.
"""

import sys
import os
import asyncio
import httpx
import json
from datetime import datetime

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

async def test_api_health():
    """Test basic API health"""
    print("🔍 Testing API Health...")
    
    try:
        # Import FastAPI app
        from api.main import app
        
        # Create test client
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            # Test root endpoint
            response = await client.get("/")
            
            if response.status_code == 200:
                print("✅ API Root endpoint responding")
                return True
            else:
                print(f"❌ API Root returned {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ API Health test failed: {str(e)}")
        return False

async def test_auth_endpoints():
    """Test authentication endpoints"""
    print("🔍 Testing Authentication...")
    
    try:
        from api.main import app
        
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            # Test registration
            user_data = {
                "email": f"test_{int(datetime.now().timestamp())}@example.com",
                "password": "testpassword123",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            
            if response.status_code == 201:
                print("✅ User registration working")
                
                # Test login
                login_response = await client.post("/api/auth/login", json={
                    "email": user_data["email"],
                    "password": user_data["password"]
                })
                
                if login_response.status_code == 200:
                    print("✅ User login working")
                    return True, login_response.json().get("access_token")
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
                    return False, None
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
                return False, None
                
    except Exception as e:
        print(f"❌ Auth test failed: {str(e)}")
        return False, None

async def test_protected_endpoints(auth_token):
    """Test protected endpoints with authentication"""
    print("🔍 Testing Protected Endpoints...")
    
    try:
        from api.main import app
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            # Test clients endpoint
            response = await client.get("/api/clients", headers=headers)
            
            if response.status_code == 200:
                print("✅ Clients endpoint protected and working")
                
                # Test creating a client
                client_data = {
                    "name": "Test Client",
                    "email": "testclient@example.com",
                    "company": "Test Company"
                }
                
                create_response = await client.post("/api/clients", json=client_data, headers=headers)
                
                if create_response.status_code == 201:
                    print("✅ Client creation working")
                    return True
                else:
                    print(f"❌ Client creation failed: {create_response.status_code}")
                    return False
            else:
                print(f"❌ Clients endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Protected endpoints test failed: {str(e)}")
        return False

async def test_database_models():
    """Test database model imports and basic functionality"""
    print("🔍 Testing Database Models...")
    
    try:
        from api.core.database import User, Client, Project, Conversation, Message
        print("✅ Database models import successfully")
        
        # Test model creation (without database)
        user = User(
            email="test@example.com",
            password_hash="hashed",
            first_name="Test",
            last_name="User"
        )
        print("✅ User model creation works")
        
        client = Client(
            name="Test Client",
            email="client@example.com"
        )
        print("✅ Client model creation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Database models test failed: {str(e)}")
        return False

def test_imports():
    """Test critical imports"""
    print("🔍 Testing Critical Imports...")
    
    try:
        # Test core imports
        from api.core.config import Settings
        print("✅ Config imports successfully")
        
        from api.core.database import init_db
        print("✅ Database imports successfully")
        
        from api.auth.jwt import JWTHandler
        print("✅ JWT handler imports successfully")
        
        # Test route imports
        from api.routes.clients import router as clients_router
        print("✅ Clients routes import successfully")
        
        from api.routes.chatbots import router as chatbots_router
        print("✅ Chatbots routes import successfully")
        
        from api.routes.conversations import router as conversations_router
        print("✅ Conversations routes import successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Imports test failed: {str(e)}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Pixel-AI-Creator Quick Test Suite")
    print("=====================================\n")
    
    test_results = []
    
    # Test imports first
    test_results.append(("Imports", test_imports()))
    
    # Test database models
    test_results.append(("Database Models", await test_database_models()))
    
    # Test API health
    test_results.append(("API Health", await test_api_health()))
    
    # Test authentication
    auth_success, auth_token = await test_auth_endpoints()
    test_results.append(("Authentication", auth_success))
    
    # Test protected endpoints if auth works
    if auth_success and auth_token:
        test_results.append(("Protected Endpoints", await test_protected_endpoints(auth_token)))
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("========================")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Ready to proceed to next TODO item.")
        return True
    else:
        print("🚫 Some tests failed. Fix issues before proceeding.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
