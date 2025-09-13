#!/usr/bin/env python3
"""
Minimal test for user registration without refresh
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


async def test_minimal_registration():
    """Test creating a user with minimal operations"""

    print("🔍 Testing Minimal User Registration...")

    # Create engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,  # Disable SQL logging for cleaner output
    )

    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        async with async_session() as session:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == "minimal@test.com")
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("⚠️  Test user already exists, deleting...")
                await session.delete(existing_user)
                await session.commit()
                print("🗑️  Deleted existing user")

            # Create new test user
            print("🧪 Creating test user (without refresh)...")
            test_user = User(
                email="minimal@test.com",
                password_hash="hashed_password_test",
                first_name="Minimal",
                last_name="Test",
                role="user",
                is_active=True,
            )

            session.add(test_user)
            await session.commit()
            print("✅ User committed to database successfully")

            # Try to query the user back (instead of refresh)
            result = await session.execute(
                select(User).where(User.email == "minimal@test.com")
            )
            created_user = result.scalar_one_or_none()

            if created_user:
                print(f"✅ User retrieved successfully: ID {created_user.id}")
                print(f"   Email: {created_user.email}")
                print(f"   Name: {created_user.first_name} {created_user.last_name}")
                print(f"   Role: {created_user.role}")

                # Clean up
                await session.delete(created_user)
                await session.commit()
                print("🗑️  Test user cleaned up")
            else:
                print("❌ Could not retrieve created user")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_minimal_registration())
