#!/usr/bin/env python3
"""
Test script for the authentication system.

This script tests:
- User registration
- User login
- Token verification
- Profile management
"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


async def test_auth_system():
    """Test the complete authentication system."""
    print("🔐 Testing Authentication System")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:

        # Test user registration
        print("1. Testing User Registration...")

        registration_data = {
            "email": f"test_user_{int(datetime.now().timestamp())}@example.com",
            "password": "SecurePassword123",
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "role": "user",
        }

        try:
            async with session.post(
                f"{BASE_URL}/auth/register", json=registration_data
            ) as response:
                if response.status == 201:
                    result = await response.json()
                    print(f"✅ Registration successful: {result['message']}")
                    print(f"   User ID: {result['user_id']}")
                    print(f"   Email: {result['email']}")
                else:
                    error = await response.json()
                    print(
                        f"❌ Registration failed: {error.get('detail', 'Unknown error')}"
                    )
                    return
        except Exception as e:
            print(f"❌ Registration error: {str(e)}")
            return

        # Test user login
        print("\n2. Testing User Login...")

        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"],
        }

        try:
            async with session.post(
                f"{BASE_URL}/auth/login", json=login_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Login successful")
                    print(f"   Token type: {result['token_type']}")
                    print(f"   Expires in: {result['expires_in']} seconds")
                    print(f"   User role: {result['role']}")

                    access_token = result["access_token"]
                else:
                    error = await response.json()
                    print(f"❌ Login failed: {error.get('detail', 'Unknown error')}")
                    return
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return

        # Test token verification and profile access
        print("\n3. Testing Profile Access...")

        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with session.get(
                f"{BASE_URL}/auth/profile", headers=headers
            ) as response:
                if response.status == 200:
                    profile = await response.json()
                    print(f"✅ Profile access successful")
                    print(f"   Name: {profile['first_name']} {profile['last_name']}")
                    print(f"   Email: {profile['email']}")
                    print(f"   Company: {profile['company_name']}")
                    print(f"   Role: {profile['role']}")
                    print(f"   Active: {profile['is_active']}")
                else:
                    error = await response.json()
                    print(
                        f"❌ Profile access failed: {error.get('detail', 'Unknown error')}"
                    )
                    return
        except Exception as e:
            print(f"❌ Profile access error: {str(e)}")
            return

        # Test profile update
        print("\n4. Testing Profile Update...")

        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "company_name": "Updated Company",
        }

        try:
            async with session.put(
                f"{BASE_URL}/auth/profile", json=update_data, headers=headers
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Profile update successful: {result['message']}")
                else:
                    error = await response.json()
                    print(
                        f"❌ Profile update failed: {error.get('detail', 'Unknown error')}"
                    )
        except Exception as e:
            print(f"❌ Profile update error: {str(e)}")

        # Test token verification
        print("\n5. Testing Token Verification...")

        try:
            async with session.post(
                f"{BASE_URL}/auth/verify-token", headers=headers
            ) as response:
                if response.status == 200:
                    profile = await response.json()
                    print(f"✅ Token verification successful")
                    print(
                        f"   Updated name: {profile['first_name']} {profile['last_name']}"
                    )
                else:
                    error = await response.json()
                    print(
                        f"❌ Token verification failed: {error.get('detail', 'Unknown error')}"
                    )
        except Exception as e:
            print(f"❌ Token verification error: {str(e)}")

        print("\n🎉 Authentication system test completed!")


async def test_invalid_scenarios():
    """Test error handling scenarios."""
    print("\n🚫 Testing Error Scenarios")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:

        # Test duplicate registration
        print("1. Testing duplicate email registration...")

        duplicate_data = {
            "email": "duplicate@example.com",
            "password": "SecurePassword123",
            "first_name": "Test",
            "last_name": "User",
        }

        # Register first time
        await session.post(f"{BASE_URL}/auth/register", json=duplicate_data)

        # Try to register again
        async with session.post(
            f"{BASE_URL}/auth/register", json=duplicate_data
        ) as response:
            if response.status == 400:
                error = await response.json()
                print(f"✅ Duplicate email properly rejected: {error['detail']}")
            else:
                print("❌ Duplicate email not properly rejected")

        # Test invalid login
        print("\n2. Testing invalid login credentials...")

        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        async with session.post(
            f"{BASE_URL}/auth/login", json=invalid_login
        ) as response:
            if response.status == 401:
                error = await response.json()
                print(f"✅ Invalid credentials properly rejected: {error['detail']}")
            else:
                print("❌ Invalid credentials not properly rejected")

        # Test invalid token
        print("\n3. Testing invalid token access...")

        invalid_headers = {"Authorization": "Bearer invalid_token_here"}

        async with session.get(
            f"{BASE_URL}/auth/profile", headers=invalid_headers
        ) as response:
            if response.status == 401:
                error = await response.json()
                print(f"✅ Invalid token properly rejected: {error['detail']}")
            else:
                print("❌ Invalid token not properly rejected")


async def main():
    """Main test function."""
    print("🧪 Pixel AI Creator - Authentication System Tests")
    print("=" * 60)

    try:
        await test_auth_system()
        await test_invalid_scenarios()

        print("\n✨ All authentication tests completed!")
        print("\nNext steps:")
        print("- Start the FastAPI server: uvicorn main:app --reload")
        print("- Run these tests to verify the authentication system")
        print("- Check API documentation at: http://localhost:8000/api/docs")

    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
