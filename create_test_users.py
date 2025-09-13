#!/usr/bin/env python3
"""
Manual Test User Creator - Workaround for broken registration

This script creates test users directly in the database
to enable manual testing while authentication is being fixed.
"""

import asyncio
import sys
import os

# Add the API directory to Python path
sys.path.insert(0, "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/api")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from core.database import User, Base
from core.config import settings
from auth.jwt import hash_password


async def create_test_users():
    """Create test users for manual testing"""

    print("🧪 Creating Test Users for Manual Testing...")

    # Create engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )

    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Test users to create
    test_users = [
        {
            "email": "admin@test.com",
            "password": "AdminPass123!",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
        },
        {
            "email": "user@test.com",
            "password": "UserPass123!",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
        },
        {
            "email": "client@test.com",
            "password": "ClientPass123!",
            "first_name": "Test",
            "last_name": "Client",
            "role": "client",
        },
    ]

    try:
        async with async_session() as session:
            for user_data in test_users:
                # Check if user exists
                result = await session.execute(
                    select(User).where(User.email == user_data["email"])
                )
                existing_user = result.scalar_one_or_none()

                if existing_user:
                    print(f"⚠️  User {user_data['email']} already exists, skipping...")
                    continue

                # Create new user
                print(f"👤 Creating user: {user_data['email']}")

                test_user = User(
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    role=user_data["role"],
                    is_active=True,
                )

                session.add(test_user)
                await session.commit()

                # Verify creation
                result = await session.execute(
                    select(User).where(User.email == user_data["email"])
                )
                created_user = result.scalar_one_or_none()

                if created_user:
                    print(
                        f"✅ Created user: {created_user.email} (ID: {created_user.id})"
                    )
                else:
                    print(f"❌ Failed to create user: {user_data['email']}")

        print("\n🎉 Test user creation complete!")
        print("\n📋 Test User Credentials:")
        print("=" * 50)
        for user_data in test_users:
            print(f"Email: {user_data['email']}")
            print(f"Password: {user_data['password']}")
            print(f"Role: {user_data['role']}")
            print("-" * 30)

        print("\n💡 Usage Instructions:")
        print("1. Use these credentials for manual testing")
        print("2. Test with frontend at http://localhost:3002")
        print("3. Test with direct API calls")
        print("4. These users bypass the broken registration system")

    except Exception as e:
        print(f"❌ Error creating test users: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_test_users())
