"""
Session database model for advanced session management.

This module provides:
- Session SQLAlchemy model
- Device tracking
- Session metadata
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()


class SessionStatus(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    BLOCKED = "blocked"


class DeviceType(str, Enum):
    """Device type enumeration."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"


class UserSession(Base):
    """User session model for advanced session management."""

    __tablename__ = "user_sessions"

    id = Column(String(255), primary_key=True)  # UUID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    refresh_token = Column(Text, nullable=False, unique=True)

    # Session metadata
    status = Column(String(20), default=SessionStatus.ACTIVE.value, nullable=False)
    session_data = Column(JSON, nullable=True)

    # Device information
    device_type = Column(String(20), default=DeviceType.UNKNOWN.value)
    device_id = Column(String(255), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    location = Column(String(255), nullable=True)  # City, Country

    # Session timing
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_activity = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Security flags
    is_suspicious = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="sessions")

    def __repr__(self):
        return (
            f"<UserSession(id='{self.id}', user_id={self.user_id}, "
            f"status='{self.status}')>"
        )

    def to_dict(self):
        """Convert session to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "device_type": self.device_type,
            "device_id": self.device_id,
            "user_agent": self.user_agent,
            "ip_address": self.ip_address,
            "location": self.location,
            "created_at": (self.created_at.isoformat() if self.created_at else None),
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
            "expires_at": (self.expires_at.isoformat() if self.expires_at else None),
            "is_suspicious": self.is_suspicious,
            "login_attempts": self.login_attempts,
            "session_data": self.session_data,
        }

    def is_expired(self):
        """Check if session is expired."""
        from datetime import datetime

        return datetime.utcnow() > self.expires_at

    def is_active(self):
        """Check if session is active and not expired."""
        return self.status == SessionStatus.ACTIVE.value and not self.is_expired()


class SessionActivity(Base):
    """Session activity log for security monitoring."""

    __tablename__ = "session_activities"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("user_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Activity details
    activity_type = Column(String(50), nullable=False)
    endpoint = Column(String(255), nullable=True)  # API endpoint accessed
    method = Column(String(10), nullable=True)  # HTTP method
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Activity metadata
    metadata = Column(JSON, nullable=True)  # Additional activity data
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Timing
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    session = relationship("UserSession")
    user = relationship("User")

    def __repr__(self):
        return (
            f"<SessionActivity(id={self.id}, type='{self.activity_type}', "
            f"session_id='{self.session_id}')>"
        )

    def to_dict(self):
        """Convert activity to dictionary representation."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "activity_type": self.activity_type,
            "endpoint": self.endpoint,
            "method": self.method,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "metadata": self.metadata,
            "success": self.success,
            "error_message": self.error_message,
            "timestamp": (self.timestamp.isoformat() if self.timestamp else None),
        }


class SecurityAlert(Base):
    """Security alerts for session monitoring."""

    __tablename__ = "security_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(255), ForeignKey("user_sessions.id"), nullable=True)

    # Alert details
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="medium")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Alert metadata
    metadata = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)

    # Alert status
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Timing
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    session = relationship("UserSession")
    resolver = relationship("User", foreign_keys=[resolved_by])

    def __repr__(self):
        return (
            f"<SecurityAlert(id={self.id}, type='{self.alert_type}', "
            f"user_id={self.user_id})>"
        )

    def to_dict(self):
        """Convert alert to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "ip_address": self.ip_address,
            "is_resolved": self.is_resolved,
            "resolved_by": self.resolved_by,
            "resolved_at": (self.resolved_at.isoformat() if self.resolved_at else None),
            "created_at": (self.created_at.isoformat() if self.created_at else None),
        }
