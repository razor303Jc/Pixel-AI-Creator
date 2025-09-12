"""
Session management service for advanced session handling.

This module provides:
- Session creation and management
- Device tracking and monitoring
- Security alerts and monitoring
- Session timeout and renewal
- Concurrent session management
"""

import uuid
import redis
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status

from core.config import get_settings
from models.user import User
from models.session import UserSession, SessionActivity, SecurityAlert
from models.session import SessionStatus, DeviceType
from auth.session_models import (
    SessionCreateRequest,
    SessionResponse,
    SessionUpdateRequest,
    SessionActivityRequest,
    SecurityAlertRequest,
    ActivityType,
    AlertSeverity,
)

settings = get_settings()


class SessionManager:
    """Advanced session management service."""

    def __init__(self, db: Session):
        self.db = db
        self.redis_client = None
        if settings.redis_url:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
            except Exception:
                pass  # Redis is optional

    def create_session(
        self,
        user_id: int,
        refresh_token: str,
        request_data: SessionCreateRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> UserSession:
        """Create a new user session."""

        # Check for concurrent session limits
        self._check_concurrent_sessions(user_id)

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Set session expiration
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

        # Create session
        session = UserSession(
            id=session_id,
            user_id=user_id,
            refresh_token=refresh_token,
            device_type=request_data.device_type.value,
            device_id=request_data.device_id,
            user_agent=user_agent or request_data.user_agent,
            ip_address=ip_address or request_data.ip_address,
            location=request_data.location,
            expires_at=expires_at,
        )

        # Check for suspicious activity
        if self._is_suspicious_login(user_id, ip_address, request_data):
            session.is_suspicious = True
            self._create_security_alert(
                user_id=user_id,
                session_id=session_id,
                alert_type="suspicious_login",
                severity=AlertSeverity.HIGH,
                title="Suspicious Login Detected",
                description=f"Login from unusual location: {request_data.location}",
                ip_address=ip_address,
            )

        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        # Log session creation activity
        self._log_activity(
            session_id=session_id,
            user_id=user_id,
            activity_type=ActivityType.LOGIN,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"device_type": request_data.device_type.value},
        )

        # Cache session in Redis if available
        if self.redis_client:
            self._cache_session(session)

        return session

    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID."""

        # Try Redis cache first
        if self.redis_client:
            cached_session = self._get_cached_session(session_id)
            if cached_session:
                return cached_session

        # Query database
        session = (
            self.db.query(UserSession).filter(UserSession.id == session_id).first()
        )

        if session and self.redis_client:
            self._cache_session(session)

        return session

    def get_user_sessions(
        self, user_id: int, active_only: bool = False, page: int = 1, per_page: int = 20
    ) -> List[UserSession]:
        """Get sessions for a user."""

        query = self.db.query(UserSession).filter(UserSession.user_id == user_id)

        if active_only:
            query = query.filter(
                and_(
                    UserSession.status == SessionStatus.ACTIVE.value,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )

        # Pagination
        offset = (page - 1) * per_page
        sessions = query.offset(offset).limit(per_page).all()

        return sessions

    def update_session(
        self, session_id: str, update_data: SessionUpdateRequest
    ) -> Optional[UserSession]:
        """Update session information."""

        session = self.get_session(session_id)
        if not session:
            return None

        # Update session data
        if update_data.session_data is not None:
            session.session_data = update_data.session_data

        if update_data.location is not None:
            session.location = update_data.location

        # Update last activity
        session.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        # Update cache
        if self.redis_client:
            self._cache_session(session)

        return session

    def refresh_session(self, session_id: str) -> Optional[UserSession]:
        """Refresh session expiration."""

        session = self.get_session(session_id)
        if not session or not session.is_active():
            return None

        # Extend session expiration
        session.expires_at = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
        session.last_activity = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session)

        # Log refresh activity
        self._log_activity(
            session_id=session_id,
            user_id=session.user_id,
            activity_type=ActivityType.REFRESH,
            metadata={"new_expiry": session.expires_at.isoformat()},
        )

        # Update cache
        if self.redis_client:
            self._cache_session(session)

        return session

    def terminate_session(self, session_id: str, reason: str = "user_logout") -> bool:
        """Terminate a session."""

        session = self.get_session(session_id)
        if not session:
            return False

        # Update session status
        session.status = SessionStatus.TERMINATED.value
        self.db.commit()

        # Log logout activity
        self._log_activity(
            session_id=session_id,
            user_id=session.user_id,
            activity_type=ActivityType.LOGOUT,
            metadata={"reason": reason},
        )

        # Remove from cache
        if self.redis_client:
            self._remove_cached_session(session_id)

        return True

    def terminate_user_sessions(
        self,
        user_id: int,
        exclude_session_id: Optional[str] = None,
        reason: str = "force_logout",
    ) -> int:
        """Terminate all sessions for a user."""

        query = self.db.query(UserSession).filter(
            and_(
                UserSession.user_id == user_id,
                UserSession.status == SessionStatus.ACTIVE.value,
            )
        )

        if exclude_session_id:
            query = query.filter(UserSession.id != exclude_session_id)

        sessions = query.all()
        terminated_count = 0

        for session in sessions:
            session.status = SessionStatus.TERMINATED.value
            self._log_activity(
                session_id=session.id,
                user_id=user_id,
                activity_type=ActivityType.LOGOUT,
                metadata={"reason": reason, "force_logout": True},
            )

            # Remove from cache
            if self.redis_client:
                self._remove_cached_session(session.id)

            terminated_count += 1

        self.db.commit()
        return terminated_count

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""

        expired_sessions = (
            self.db.query(UserSession)
            .filter(
                and_(
                    UserSession.status == SessionStatus.ACTIVE.value,
                    UserSession.expires_at < datetime.utcnow(),
                )
            )
            .all()
        )

        cleaned_count = 0
        for session in expired_sessions:
            session.status = SessionStatus.EXPIRED.value

            # Remove from cache
            if self.redis_client:
                self._remove_cached_session(session.id)

            cleaned_count += 1

        self.db.commit()
        return cleaned_count

    def get_session_statistics(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get session statistics."""

        query = self.db.query(UserSession)
        if user_id:
            query = query.filter(UserSession.user_id == user_id)

        total_sessions = query.count()
        active_sessions = query.filter(
            and_(
                UserSession.status == SessionStatus.ACTIVE.value,
                UserSession.expires_at > datetime.utcnow(),
            )
        ).count()

        expired_sessions = query.filter(
            UserSession.status == SessionStatus.EXPIRED.value
        ).count()

        terminated_sessions = query.filter(
            UserSession.status == SessionStatus.TERMINATED.value
        ).count()

        blocked_sessions = query.filter(
            UserSession.status == SessionStatus.BLOCKED.value
        ).count()

        suspicious_sessions = query.filter(UserSession.is_suspicious == True).count()

        unique_devices = query.with_entities(
            func.count(func.distinct(UserSession.device_id))
        ).scalar()

        unique_locations = query.with_entities(
            func.count(func.distinct(UserSession.location))
        ).scalar()

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions,
            "terminated_sessions": terminated_sessions,
            "blocked_sessions": blocked_sessions,
            "suspicious_sessions": suspicious_sessions,
            "unique_devices": unique_devices or 0,
            "unique_locations": unique_locations or 0,
        }

    def _check_concurrent_sessions(self, user_id: int) -> None:
        """Check concurrent session limits."""

        active_sessions = (
            self.db.query(UserSession)
            .filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.status == SessionStatus.ACTIVE.value,
                    UserSession.expires_at > datetime.utcnow(),
                )
            )
            .count()
        )

        max_concurrent = getattr(settings, "max_concurrent_sessions", 5)

        if active_sessions >= max_concurrent:
            # Terminate oldest session
            oldest_session = (
                self.db.query(UserSession)
                .filter(
                    and_(
                        UserSession.user_id == user_id,
                        UserSession.status == SessionStatus.ACTIVE.value,
                        UserSession.expires_at > datetime.utcnow(),
                    )
                )
                .order_by(UserSession.created_at.asc())
                .first()
            )

            if oldest_session:
                self.terminate_session(oldest_session.id, "concurrent_limit_exceeded")

    def _is_suspicious_login(
        self,
        user_id: int,
        ip_address: Optional[str],
        request_data: SessionCreateRequest,
    ) -> bool:
        """Check if login is suspicious."""

        if not ip_address:
            return False

        # Check for new location
        recent_sessions = (
            self.db.query(UserSession)
            .filter(
                and_(
                    UserSession.user_id == user_id,
                    UserSession.created_at > datetime.utcnow() - timedelta(days=30),
                )
            )
            .all()
        )

        known_ips = {s.ip_address for s in recent_sessions if s.ip_address}
        known_locations = {s.location for s in recent_sessions if s.location}

        # Suspicious if new IP and new location
        return (
            ip_address not in known_ips
            and request_data.location
            and request_data.location not in known_locations
        )

    def _log_activity(
        self,
        session_id: str,
        user_id: int,
        activity_type: ActivityType,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> None:
        """Log session activity."""

        activity = SessionActivity(
            session_id=session_id,
            user_id=user_id,
            activity_type=activity_type.value,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            activity_metadata=metadata,
            success=success,
            error_message=error_message,
        )

        self.db.add(activity)
        self.db.commit()

    def _create_security_alert(
        self,
        user_id: int,
        alert_type: str,
        severity: AlertSeverity,
        title: str,
        description: str,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SecurityAlert:
        """Create a security alert."""

        alert = SecurityAlert(
            user_id=user_id,
            session_id=session_id,
            alert_type=alert_type,
            severity=severity.value,
            title=title,
            description=description,
            ip_address=ip_address,
            alert_metadata=metadata,
        )

        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        return alert

    def _cache_session(self, session: UserSession) -> None:
        """Cache session in Redis."""
        if not self.redis_client:
            return

        try:
            session_data = {
                "id": session.id,
                "user_id": session.user_id,
                "status": session.status,
                "expires_at": session.expires_at.isoformat(),
            }

            # Cache for session duration
            ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                self.redis_client.setex(f"session:{session.id}", ttl, str(session_data))
        except Exception:
            pass  # Cache failures shouldn't break functionality

    def _get_cached_session(self, session_id: str) -> Optional[UserSession]:
        """Get session from Redis cache."""
        if not self.redis_client:
            return None

        try:
            cached_data = self.redis_client.get(f"session:{session_id}")
            if cached_data:
                # Return database session if cache hit (for full data)
                return (
                    self.db.query(UserSession)
                    .filter(UserSession.id == session_id)
                    .first()
                )
        except Exception:
            pass

        return None

    def _remove_cached_session(self, session_id: str) -> None:
        """Remove session from Redis cache."""
        if not self.redis_client:
            return

        try:
            self.redis_client.delete(f"session:{session_id}")
        except Exception:
            pass
