#!/usr/bin/env python3
"""
Create session management tables in the database.

This script creates the required tables for the session management system:
- user_sessions: Store active user sessions with device tracking
- session_activities: Log all session activities for security monitoring
- security_alerts: Store security alerts and notifications
"""

import sys
import os

# Add the api directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "api"))

from sqlalchemy import create_engine, text
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_session_tables():
    """Create session management tables using raw SQL."""
    try:
        # Get database URL from settings
        database_url = settings.database_url
        logger.info("Connecting to database...")

        # Create engine (synchronous for migration)
        sync_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        if not sync_url.startswith("postgresql://"):
            sync_url = database_url.replace("postgresql://", "postgresql://")

        engine = create_engine(sync_url)

        # Create the session tables using raw SQL
        logger.info("Creating session management tables...")

        with engine.connect() as conn:
            # Create user_sessions table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    device_type VARCHAR(20) DEFAULT 'unknown',
                    device_name VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    location VARCHAR(255),
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                    terminated_at TIMESTAMP WITH TIME ZONE,
                    termination_reason VARCHAR(100)
                );
            """
                )
            )

            # Create session_activities table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS session_activities (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL REFERENCES user_sessions(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    activity_type VARCHAR(50) NOT NULL,
                    endpoint VARCHAR(255),
                    method VARCHAR(10),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    activity_metadata JSONB,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """
                )
            )

            # Create security_alerts table
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    session_id VARCHAR(255) REFERENCES user_sessions(id),
                    alert_type VARCHAR(50) NOT NULL,
                    severity VARCHAR(20) DEFAULT 'medium',
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    alert_metadata JSONB,
                    ip_address VARCHAR(45),
                    is_resolved BOOLEAN DEFAULT FALSE,
                    resolved_by INTEGER,
                    resolved_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """
                )
            )

            conn.commit()

        logger.info("Session tables created successfully!")

        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('user_sessions', 'session_activities', 'security_alerts')
                ORDER BY table_name;
            """
                )
            )

            tables = [row[0] for row in result]
            logger.info(f"Created tables: {tables}")

            if len(tables) == 3:
                logger.info("✅ All session management tables created!")
                return True
            else:
                logger.error(f"❌ Expected 3 tables, found {len(tables)}")
                return False

    except Exception as e:
        logger.error(f"❌ Error creating session tables: {e}")
        return False


if __name__ == "__main__":
    success = create_session_tables()
    sys.exit(0 if success else 1)
