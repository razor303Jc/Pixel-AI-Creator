#!/usr/bin/env python3
"""
Quick test to diagnose authentication database issues
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


async def test_user_creation():
    """Test creating a user directly with the database"""

    print("🔍 Testing User Database Operations...")

    # Create engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,  # Show SQL queries
    )

    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    try:
        # Create tables if they don't exist
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("✅ Database tables created/verified")

        # Test user creation
        async with async_session() as session:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print("⚠️  Test user already exists, deleting...")
                await session.delete(existing_user)
                await session.commit()

            # Create new test user
            print("🧪 Creating test user...")
            test_user = User(
                email="test@example.com",
                password_hash="hashed_password_here",
                first_name="Test",
                last_name="User",
                role="user",
                is_active=True,
            )

            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)

            print(f"✅ User created successfully: ID {test_user.id}")
            print(f"   Email: {test_user.email}")
            print(f"   Name: {test_user.first_name} {test_user.last_name}")
            print(f"   Role: {test_user.role}")

            # Clean up
            await session.delete(test_user)
            await session.commit()
            print("🗑️  Test user cleaned up")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback

        traceback.print_exc()

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_user_creation())
