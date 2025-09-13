#!/usr/bin/env python3
"""
Reset database to clean state - ONLY for development!
"""

import asyncio
import sys
import os

# Add the API directory to Python path
sys.path.insert(0, "/home/jc/Documents/ChatBot-Project/Pixel-AI-Creator/api")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
from core.database import Base
from core.config import settings


async def reset_database():
    """Drop all tables and recreate them"""

    print("🚨 RESETTING DATABASE - ALL DATA WILL BE LOST!")
    print("This is for development only!")

    # Create engine
    engine = create_async_engine(
        settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=True,
    )

    try:
        # Drop all tables
        async with engine.begin() as conn:
            print("🗑️  Dropping all tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("✅ All tables dropped")

            print("🏗️  Creating clean tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Clean tables created")

        print("🎉 Database reset complete!")

    except Exception as e:
        print(f"❌ Error resetting database: {str(e)}")
        import traceback

        traceback.print_exc()

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_database())
