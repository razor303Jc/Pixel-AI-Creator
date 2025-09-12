"""
Session management Pydantic models for API requests and responses.

This module provides:
- Session creation and validation models
- Device tracking models
- Security monitoring models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


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


class ActivityType(str, Enum):
    """Session activity types."""

    LOGIN = "login"
    LOGOUT = "logout"
    REFRESH = "refresh"
    API_CALL = "api_call"
    PASSWORD_CHANGE = "password_change"
    PROFILE_UPDATE = "profile_update"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AlertSeverity(str, Enum):
    """Security alert severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SessionCreateRequest(BaseModel):
    """Request model for creating a new session."""

    device_type: Optional[DeviceType] = DeviceType.UNKNOWN
    device_id: Optional[str] = Field(None, max_length=255)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)
    location: Optional[str] = Field(None, max_length=255)

    class Config:
        schema_extra = {
            "example": {
                "device_type": "desktop",
                "device_id": "device-123",
                "user_agent": "Mozilla/5.0...",
                "ip_address": "192.168.1.1",
                "location": "New York, US",
            }
        }


class SessionResponse(BaseModel):
    """Response model for session information."""

    id: str
    user_id: int
    status: SessionStatus
    device_type: DeviceType
    device_id: Optional[str]
    user_agent: Optional[str]
    ip_address: Optional[str]
    location: Optional[str]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_suspicious: bool
    login_attempts: int
    session_data: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class SessionUpdateRequest(BaseModel):
    """Request model for updating session."""

    session_data: Optional[Dict[str, Any]] = None
    location: Optional[str] = Field(None, max_length=255)

    class Config:
        schema_extra = {
            "example": {
                "session_data": {"theme": "dark", "language": "en"},
                "location": "San Francisco, US",
            }
        }


class SessionActivityRequest(BaseModel):
    """Request model for logging session activity."""

    activity_type: ActivityType
    endpoint: Optional[str] = Field(None, max_length=255)
    method: Optional[str] = Field(None, max_length=10)
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "activity_type": "api_call",
                "endpoint": "/api/users/profile",
                "method": "GET",
                "metadata": {"response_time": 150},
                "success": True,
            }
        }


class SessionActivityResponse(BaseModel):
    """Response model for session activity."""

    id: int
    session_id: str
    user_id: int
    activity_type: ActivityType
    endpoint: Optional[str]
    method: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    metadata: Optional[Dict[str, Any]]
    success: bool
    error_message: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class SecurityAlertRequest(BaseModel):
    """Request model for creating security alerts."""

    alert_type: str = Field(..., max_length=50)
    severity: AlertSeverity = AlertSeverity.MEDIUM
    title: str = Field(..., max_length=255)
    description: str
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        schema_extra = {
            "example": {
                "alert_type": "suspicious_login",
                "severity": "high",
                "title": "Suspicious login attempt",
                "description": "Login from unusual location",
                "metadata": {"ip": "192.168.1.100", "country": "Unknown"},
            }
        }


class SecurityAlertResponse(BaseModel):
    """Response model for security alerts."""

    id: int
    user_id: int
    session_id: Optional[str]
    alert_type: str
    severity: AlertSeverity
    title: str
    description: str
    metadata: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    is_resolved: bool
    resolved_by: Optional[int]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Response model for listing sessions."""

    sessions: List[SessionResponse]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool

    class Config:
        schema_extra = {
            "example": {
                "sessions": [],
                "total": 10,
                "page": 1,
                "per_page": 20,
                "has_next": False,
                "has_prev": False,
            }
        }


class SessionStatsResponse(BaseModel):
    """Response model for session statistics."""

    total_sessions: int
    active_sessions: int
    expired_sessions: int
    terminated_sessions: int
    blocked_sessions: int
    suspicious_sessions: int
    unique_devices: int
    unique_locations: int
    recent_activities: int

    class Config:
        schema_extra = {
            "example": {
                "total_sessions": 150,
                "active_sessions": 45,
                "expired_sessions": 90,
                "terminated_sessions": 10,
                "blocked_sessions": 5,
                "suspicious_sessions": 3,
                "unique_devices": 25,
                "unique_locations": 15,
                "recent_activities": 200,
            }
        }


class DeviceSessionsResponse(BaseModel):
    """Response model for device-specific sessions."""

    device_id: str
    device_type: DeviceType
    sessions: List[SessionResponse]
    total_sessions: int
    active_sessions: int

    class Config:
        from_attributes = True


class SessionTimeoutRequest(BaseModel):
    """Request model for session timeout configuration."""

    timeout_minutes: int = Field(..., ge=5, le=1440)  # 5 minutes to 24 hours
    extend_on_activity: bool = True

    @validator("timeout_minutes")
    def validate_timeout(cls, v):
        if v < 5:
            raise ValueError("Timeout must be at least 5 minutes")
        if v > 1440:
            raise ValueError("Timeout cannot exceed 24 hours")
        return v

    class Config:
        schema_extra = {"example": {"timeout_minutes": 60, "extend_on_activity": True}}
