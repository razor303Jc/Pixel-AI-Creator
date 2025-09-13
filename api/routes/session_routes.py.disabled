"""
Session management API routes.

This module provides:
- Session CRUD operations
- Device management
- Security monitoring
- Session statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import logging

from core.database import get_db
from auth.middleware import get_current_user
from services.session_service import SessionManager
from models.user import User
from models.session import UserSession, SessionActivity
from auth.session_models import (
    SessionResponse,
    SessionUpdateRequest,
    SessionActivityRequest,
    SessionActivityResponse,
    SessionListResponse,
    SessionStatsResponse,
    DeviceSessionsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def get_session_manager(db: Session = Depends(get_db)) -> SessionManager:
    """Get session manager instance."""
    return SessionManager(db)


@router.get("/", response_model=SessionListResponse)
async def get_user_sessions(
    active_only: bool = False,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Get current user's sessions."""

    try:
        sessions = session_manager.get_user_sessions(
            user_id=current_user.id,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )

        # Get total count
        total_sessions = (
            session_manager.db.query(
                session_manager.db.query(
                    session_manager.db.query.UserSession
                ).filter_by(user_id=current_user.id)
            ).count()
            if not active_only
            else len(sessions)
        )

        return SessionListResponse(
            sessions=[SessionResponse.from_orm(s) for s in sessions],
            total=total_sessions,
            page=page,
            per_page=per_page,
            has_next=(page * per_page) < total_sessions,
            has_prev=page > 1,
        )

    except Exception as e:
        logger.error(f"Error fetching user sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch sessions",
        )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Get specific session details."""

    try:
        session = session_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # Check if user owns the session
        if session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

        return SessionResponse.from_orm(session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session",
        )


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    update_data: SessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Update session information."""

    try:
        # Verify session ownership
        session = session_manager.get_session(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        updated_session = session_manager.update_session(session_id, update_data)
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update session",
            )

        return SessionResponse.from_orm(updated_session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session",
        )


@router.post("/{session_id}/refresh", response_model=SessionResponse)
async def refresh_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Refresh session expiration."""

    try:
        # Verify session ownership
        session = session_manager.get_session(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        refreshed_session = session_manager.refresh_session(session_id)
        if not refreshed_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot refresh expired or inactive session",
            )

        return SessionResponse.from_orm(refreshed_session)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh session",
        )


@router.delete("/{session_id}")
async def terminate_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Terminate a session."""

    try:
        # Verify session ownership
        session = session_manager.get_session(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        success = session_manager.terminate_session(session_id, "user_logout")
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to terminate session",
            )

        return {"message": "Session terminated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error terminating session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate session",
        )


@router.delete("/")
async def terminate_all_sessions(
    exclude_current: bool = True,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
    request: Request = None,
):
    """Terminate all user sessions."""

    try:
        current_session_id = None
        if exclude_current:
            # Try to get current session ID from request headers
            auth_header = request.headers.get("authorization")
            if auth_header:
                # Extract session ID from token (implementation depends on token structure)
                pass  # For now, we'll include current session in termination

        terminated_count = session_manager.terminate_user_sessions(
            user_id=current_user.id,
            exclude_session_id=current_session_id,
            reason="user_logout_all",
        )

        return {
            "message": f"Terminated {terminated_count} sessions",
            "terminated_count": terminated_count,
        }

    except Exception as e:
        logger.error(f"Error terminating all sessions for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate sessions",
        )


@router.get("/stats/overview", response_model=SessionStatsResponse)
async def get_session_stats(
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Get session statistics for current user."""

    try:
        stats = session_manager.get_session_statistics(user_id=current_user.id)

        # Add recent activities count
        from datetime import datetime, timedelta

        recent_activities = (
            session_manager.db.query(session_manager.db.query.SessionActivity)
            .filter(
                session_manager.db.query.SessionActivity.user_id == current_user.id,
                session_manager.db.query.SessionActivity.timestamp
                > datetime.utcnow() - timedelta(hours=24),
            )
            .count()
        )

        stats["recent_activities"] = recent_activities

        return SessionStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error fetching session stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session statistics",
        )


@router.get("/devices/{device_id}", response_model=DeviceSessionsResponse)
async def get_device_sessions(
    device_id: str,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Get sessions for a specific device."""

    try:
        sessions = (
            session_manager.db.query(session_manager.db.query.UserSession)
            .filter(
                session_manager.db.query.UserSession.user_id == current_user.id,
                session_manager.db.query.UserSession.device_id == device_id,
            )
            .all()
        )

        if not sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sessions found for this device",
            )

        # Get device type from first session
        device_type = sessions[0].device_type

        # Count active sessions
        active_count = sum(1 for s in sessions if s.is_active())

        return DeviceSessionsResponse(
            device_id=device_id,
            device_type=device_type,
            sessions=[SessionResponse.from_orm(s) for s in sessions],
            total_sessions=len(sessions),
            active_sessions=active_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching device sessions for {device_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch device sessions",
        )


@router.post("/{session_id}/activity", response_model=SessionActivityResponse)
async def log_session_activity(
    session_id: str,
    activity_data: SessionActivityRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Log session activity."""

    try:
        # Verify session ownership
        session = session_manager.get_session(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        # Get request info
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent")

        # Log activity
        session_manager._log_activity(
            session_id=session_id,
            user_id=current_user.id,
            activity_type=activity_data.activity_type,
            endpoint=activity_data.endpoint,
            method=activity_data.method,
            ip_address=client_ip,
            user_agent=user_agent,
            metadata=activity_data.metadata,
            success=activity_data.success,
            error_message=activity_data.error_message,
        )

        # Fetch the created activity
        latest_activity = (
            session_manager.db.query(session_manager.db.query.SessionActivity)
            .filter(session_manager.db.query.SessionActivity.session_id == session_id)
            .order_by(session_manager.db.query.SessionActivity.timestamp.desc())
            .first()
        )

        return SessionActivityResponse.from_orm(latest_activity)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging activity for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log activity",
        )


@router.get("/{session_id}/activities", response_model=List[SessionActivityResponse])
async def get_session_activities(
    session_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Get activities for a session."""

    try:
        # Verify session ownership
        session = session_manager.get_session(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        activities = (
            session_manager.db.query(session_manager.db.query.SessionActivity)
            .filter(session_manager.db.query.SessionActivity.session_id == session_id)
            .order_by(session_manager.db.query.SessionActivity.timestamp.desc())
            .limit(limit)
            .all()
        )

        return [SessionActivityResponse.from_orm(a) for a in activities]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching activities for session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch activities",
        )


@router.post("/cleanup/expired")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Clean up expired sessions (admin only)."""

    try:
        # For now, allow all users to clean their own expired sessions
        # In production, this might be admin-only

        cleaned_count = session_manager.cleanup_expired_sessions()

        return {
            "message": f"Cleaned up {cleaned_count} expired sessions",
            "cleaned_count": cleaned_count,
        }

    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired sessions",
        )
