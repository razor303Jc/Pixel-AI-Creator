"""
Session management API routes.

This module provides:
- Session CRUD operations
- Device management
- Security monitoring
- Session statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from core.database import get_db
from auth.middleware import get_current_user_model
from services.session_service import SessionManager
from models.user import User
from auth.session_models import (
    SessionResponse,
    SessionUpdateRequest,
    SessionListResponse,
    SessionStatsResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_manager(db: Session = Depends(get_db)) -> SessionManager:
    """Get session manager instance."""
    return SessionManager(db)


@router.get("/", response_model=SessionListResponse)
async def get_user_sessions(
    active_only: bool = False,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user_model),
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

        # Simple count for now
        total_sessions = len(sessions)

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
    current_user: User = Depends(get_current_user_model),
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
    current_user: User = Depends(get_current_user_model),
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
    current_user: User = Depends(get_current_user_model),
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
    current_user: User = Depends(get_current_user_model),
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
    current_user: User = Depends(get_current_user_model),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Terminate all user sessions."""

    try:
        current_session_id = None
        # For now, we'll handle session ID extraction later

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
        logger.error(f"Error terminating all sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to terminate sessions",
        )


@router.get("/stats/overview", response_model=SessionStatsResponse)
async def get_session_stats(
    current_user: User = Depends(get_current_user_model),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Get session statistics for current user."""

    try:
        stats = session_manager.get_session_statistics(user_id=current_user.id)

        # Add recent activities count (simplified for now)
        stats["recent_activities"] = 0

        return SessionStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Error fetching session stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session statistics",
        )


@router.post("/cleanup/expired")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user_model),
    session_manager: SessionManager = Depends(get_session_manager),
):
    """Clean up expired sessions."""

    try:
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
