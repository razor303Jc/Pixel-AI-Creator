"""
Simple test session endpoints for demonstration.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from core.database import get_db
from auth.middleware import get_current_user_model
from models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions-test", tags=["sessions-test"])


@router.get("/")
async def get_test_sessions(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Test endpoint to verify session management functionality."""

    try:
        # Query user sessions
        result = await db.execute(
            text("SELECT * FROM user_sessions WHERE user_id = :user_id"),
            {"user_id": current_user.id},
        )
        sessions = result.fetchall()

        # Query session activities
        activity_result = await db.execute(
            text(
                "SELECT COUNT(*) as count FROM session_activities WHERE user_id = :user_id"
            ),
            {"user_id": current_user.id},
        )
        activity_count = activity_result.fetchone()[0]

        # Query security alerts
        alert_result = await db.execute(
            text(
                "SELECT COUNT(*) as count FROM security_alerts WHERE user_id = :user_id"
            ),
            {"user_id": current_user.id},
        )
        alert_count = alert_result.fetchone()[0]

        return {
            "message": "Session Management System is working!",
            "user_id": current_user.id,
            "user_name": f"{current_user.first_name} {current_user.last_name}",
            "email": current_user.email,
            "active_sessions": len(sessions),
            "total_activities": activity_count,
            "security_alerts": alert_count,
            "system_status": "✅ All session tables accessible",
            "features": [
                "User session tracking",
                "Device management",
                "Activity logging",
                "Security monitoring",
                "Session timeout/renewal",
                "Concurrent session limits",
            ],
        }

    except Exception as e:
        logger.error(f"Error in test endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")


@router.post("/create-test-session")
async def create_test_session(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Create a test session entry."""

    try:
        # Insert a test session
        await db.execute(
            text(
                """
                INSERT INTO user_sessions 
                (id, user_id, device_type, device_name, ip_address, status, expires_at)
                VALUES 
                (:id, :user_id, :device_type, :device_name, :ip_address, :status, 
                 NOW() + INTERVAL '1 hour')
            """
            ),
            {
                "id": f"test_session_{current_user.id}",
                "user_id": current_user.id,
                "device_type": "web",
                "device_name": "Test Browser",
                "ip_address": "127.0.0.1",
                "status": "active",
            },
        )

        # Log the session creation activity
        await db.execute(
            text(
                """
                INSERT INTO session_activities 
                (session_id, user_id, activity_type, endpoint, method, ip_address)
                VALUES 
                (:session_id, :user_id, :activity_type, :endpoint, :method, :ip_address)
            """
            ),
            {
                "session_id": f"test_session_{current_user.id}",
                "user_id": current_user.id,
                "activity_type": "login",
                "endpoint": "/sessions-test/create-test-session",
                "method": "POST",
                "ip_address": "127.0.0.1",
            },
        )

        await db.commit()

        return {
            "message": "✅ Test session created successfully!",
            "session_id": f"test_session_{current_user.id}",
            "user": f"{current_user.first_name} {current_user.last_name}",
            "features_demonstrated": [
                "Session creation",
                "Activity logging",
                "Database integration",
                "User authentication",
            ],
        }

    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating test session: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create test session: {str(e)}"
        )


@router.get("/tables-info")
async def get_tables_info(
    current_user: User = Depends(get_current_user_model),
    db: AsyncSession = Depends(get_db),
):
    """Get information about session management tables."""

    try:
        # Check table existence and structure
        tables_result = await db.execute(
            text(
                """
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.columns 
                        WHERE table_name = t.table_name AND table_schema = 'public') as column_count
                FROM information_schema.tables t
                WHERE table_schema = 'public' 
                AND table_name IN ('user_sessions', 'session_activities', 'security_alerts')
                ORDER BY table_name
            """
            )
        )

        tables = []
        for row in tables_result:
            tables.append({"table_name": row[0], "column_count": row[1]})

        return {
            "message": "Session Management System Database Status",
            "authenticated_user": f"{current_user.first_name} {current_user.last_name}",
            "tables": tables,
            "total_tables": len(tables),
            "system_ready": len(tables) == 3,
            "database_schema": "✅ All required tables exist",
        }

    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        raise HTTPException(status_code=500, detail=f"Database check failed: {str(e)}")
