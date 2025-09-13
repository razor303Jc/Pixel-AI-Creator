#!/usr/bin/env python3
"""
Manually drop problematic tables
"""

import asyncio
import sys
import os

# Add the API directory to Python path
sys.path.insert(0, "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/api")

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from core.config import settings


async def drop_advanced_tables():
    """Drop all advanced authentication tables manually"""

    print("🧹 Dropping advanced authentication tables manually...")

    # Create engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )

    # Tables to drop (in reverse dependency order)
    tables_to_drop = [
        "session_activities",
        "security_alerts",
        "mfa_configurations",
        "social_accounts",
        "login_attempts",
        "security_events",
        "password_history",
        "device_tokens",
        "account_lockouts",
        "user_sessions",
    ]

    try:
        async with engine.begin() as conn:
            for table in tables_to_drop:
                try:
                    print(f"  Dropping {table}...")
                    await conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"  ✅ {table} dropped")
                except Exception as e:
                    print(f"  ⚠️  Could not drop {table}: {e}")

            print("🎉 Advanced tables cleanup complete!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(drop_advanced_tables())
