#!/usr/bin/env python3
"""
Quick Test User Creator - Simple version with bcrypt hashing
"""

import asyncio
import sys
import bcrypt

# Add the API directory to Python path
sys.path.insert(0, "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/api")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.config import settings


def bcrypt_hash_password(password: str) -> str:
    """Proper bcrypt password hashing matching the auth system"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


async def create_simple_test_user():
    """Create a simple test user directly with SQL"""

    print("🧪 Creating Simple Test User...")

    # Create engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )

    try:
        async with engine.begin() as conn:
            # Delete existing test user first
            await conn.execute(
                text("DELETE FROM users WHERE email = 'test@manual.com'")
            )

            # Create test user with bcrypt hashing
            await conn.execute(
                text(
                    """
                    INSERT INTO users (
                        email, password_hash, first_name, last_name,
                        role, is_active, created_at, updated_at
                    ) VALUES (
                        'test@manual.com',
                        :password_hash,
                        'Manual',
                        'Test',
                        'user',
                        true,
                        NOW(),
                        NOW()
                    )
                """
                ),
                {"password_hash": bcrypt_hash_password("TestPass123!")},
            )

            print("✅ Test user created successfully with bcrypt hashing!")
            print("\n📋 Test Credentials:")
            print("Email: test@manual.com")
            print("Password: TestPass123!")
            print("\n💡 Note: Uses bcrypt hashing compatible with auth system")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_simple_test_user())
