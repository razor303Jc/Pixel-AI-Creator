"""
Database migration for advanced authentication features
Creates tables for MFA, social login, security events, and session management
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from core.database import Base, DATABASE_URL
from auth.advanced_database_models import (
    MFAConfiguration,
    SocialAccount,
    UserSession,
    LoginAttempt,
    SecurityEvent,
    PasswordHistory,
    DeviceToken,
    AccountLockout,
)
import logging

logger = logging.getLogger(__name__)


async def create_advanced_auth_tables():
    """Create all advanced authentication tables"""
    try:
        # Create async engine
        engine = create_async_engine(DATABASE_URL, echo=True)

        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating advanced authentication tables...")

            # Create tables
            await conn.run_sync(Base.metadata.create_all)

            logger.info("Advanced authentication tables created successfully")

        await engine.dispose()

    except Exception as e:
        logger.error(f"Error creating advanced auth tables: {e}")
        raise


async def add_user_relationships():
    """Add relationship columns to existing users table if needed"""
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)

        async with engine.begin() as conn:
            logger.info("Checking user table for advanced auth columns...")

            # Add any missing columns to users table
            migration_queries = [
                # Add security-related columns to users table
                """
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
                ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP NULL,
                ADD COLUMN IF NOT EXISTS last_password_change TIMESTAMP NULL,
                ADD COLUMN IF NOT EXISTS mfa_enabled BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS security_score INTEGER DEFAULT 50,
                ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP NULL,
                ADD COLUMN IF NOT EXISTS phone_verified_at TIMESTAMP NULL
                """,
                # Create indexes for performance
                """
                CREATE INDEX IF NOT EXISTS idx_users_email_verified 
                ON users(email, is_verified)
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_users_locked_until 
                ON users(locked_until) WHERE locked_until IS NOT NULL
                """,
                """
                CREATE INDEX IF NOT EXISTS idx_users_mfa_enabled 
                ON users(mfa_enabled) WHERE mfa_enabled = TRUE
                """,
            ]

            for query in migration_queries:
                try:
                    await conn.execute(text(query))
                    logger.info(f"Executed migration query successfully")
                except Exception as e:
                    logger.warning(f"Migration query failed (may already exist): {e}")

            logger.info("User table migration completed")

        await engine.dispose()

    except Exception as e:
        logger.error(f"Error adding user relationships: {e}")
        raise


async def create_initial_data():
    """Create initial data for advanced authentication"""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            logger.info("Creating initial advanced auth data...")

            # Check if we have any users
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.scalar()

            if user_count > 0:
                logger.info(f"Found {user_count} existing users")

                # Update existing users with default security settings
                await session.execute(
                    text(
                        """
                    UPDATE users 
                    SET 
                        failed_login_attempts = 0,
                        mfa_enabled = FALSE,
                        security_score = 50,
                        last_password_change = updated_at
                    WHERE 
                        failed_login_attempts IS NULL 
                        OR mfa_enabled IS NULL 
                        OR security_score IS NULL
                """
                    )
                )

                await session.commit()
                logger.info("Updated existing users with default security settings")

            logger.info("Initial advanced auth data created successfully")

        await engine.dispose()

    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
        raise


async def verify_tables():
    """Verify that all tables were created successfully"""
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)

        async with engine.begin() as conn:
            # Check if all tables exist
            tables_to_check = [
                "mfa_configurations",
                "social_accounts",
                "user_sessions",
                "login_attempts",
                "security_events",
                "password_history",
                "device_tokens",
                "account_lockouts",
            ]

            for table in tables_to_check:
                result = await conn.execute(
                    text(
                        f"""
                    SELECT EXISTS (
                        SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_name = '{table}'
                    )
                """
                    )
                )

                exists = result.scalar()
                if exists:
                    logger.info(f"✅ Table '{table}' exists")
                else:
                    logger.error(f"❌ Table '{table}' does not exist")

            logger.info("Table verification completed")

        await engine.dispose()

    except Exception as e:
        logger.error(f"Error verifying tables: {e}")
        raise


async def run_migration():
    """Run the complete migration"""
    try:
        logger.info("Starting advanced authentication migration...")

        # Step 1: Create new tables
        await create_advanced_auth_tables()

        # Step 2: Add relationship columns to users table
        await add_user_relationships()

        # Step 3: Create initial data
        await create_initial_data()

        # Step 4: Verify everything was created
        await verify_tables()

        logger.info("✅ Advanced authentication migration completed successfully!")

    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


if __name__ == "__main__":
    # Run the migration
    asyncio.run(run_migration())
