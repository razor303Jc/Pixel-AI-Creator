"""
Database models for advanced authentication features
MFA, social login, security events, and session management
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    JSON,
    BigInteger,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
import uuid

from core.database import Base


class MFAMethod(str, Enum):
    """Multi-Factor Authentication methods"""

    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BACKUP_CODES = "backup_codes"


class SocialProvider(str, Enum):
    """Social login providers"""

    GOOGLE = "google"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    MICROSOFT = "microsoft"


class DeviceType(str, Enum):
    """Device types for tracking"""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"


class SecurityEventType(str, Enum):
    """Security event types"""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    MFA_SETUP = "mfa_setup"
    MFA_DISABLED = "mfa_disabled"
    SOCIAL_ACCOUNT_LINKED = "social_account_linked"
    SOCIAL_ACCOUNT_UNLINKED = "social_account_unlinked"
    SUSPICIOUS_LOGIN = "suspicious_login"
    ACCOUNT_LOCKED = "account_locked"
    PASSWORD_RESET = "password_reset"


class MFAConfiguration(Base):
    """User MFA configuration"""

    __tablename__ = "mfa_configurations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    method = Column(SQLEnum(MFAMethod), nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False)
    secret_key = Column(Text, nullable=True)  # For TOTP
    phone_number = Column(String(20), nullable=True)  # For SMS
    backup_codes = Column(JSON, nullable=True)  # Array of backup codes
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="mfa_configurations")

    __table_args__ = (Index("idx_mfa_user_method", "user_id", "method"),)


class SocialAccount(Base):
    """Social media account links"""

    __tablename__ = "social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(SQLEnum(SocialProvider), nullable=False)
    provider_user_id = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    name = Column(String(255), nullable=True)
    avatar_url = Column(Text, nullable=True)
    access_token = Column(Text, nullable=True)  # Encrypted in production
    refresh_token = Column(Text, nullable=True)  # Encrypted in production
    token_expires_at = Column(DateTime, nullable=True)
    profile_data = Column(JSON, nullable=True)  # Additional profile info
    is_active = Column(Boolean, default=True, nullable=False)
    linked_at = Column(DateTime, default=func.now(), nullable=False)
    last_used = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="social_accounts")

    __table_args__ = (
        Index("idx_social_provider_user", "provider", "provider_user_id"),
        Index("idx_social_user_provider", "user_id", "provider"),
    )


class UserSession(Base):
    """User session tracking"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    device_fingerprint = Column(String(255), nullable=True)
    device_type = Column(SQLEnum(DeviceType), default=DeviceType.UNKNOWN)
    device_name = Column(String(255), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    location_country = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=func.now(), nullable=False)
    logout_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")

    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_expires", "expires_at"),
    )


class LoginAttempt(Base):
    """Login attempt tracking"""

    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    mfa_required = Column(Boolean, default=False, nullable=False)
    mfa_completed = Column(Boolean, default=False, nullable=False)
    location_country = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)
    blocked = Column(Boolean, default=False, nullable=False)
    risk_score = Column(Integer, default=0, nullable=False)  # 0-100
    attempted_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="login_attempts")

    __table_args__ = (
        Index("idx_login_email_time", "email", "attempted_at"),
        Index("idx_login_ip_time", "ip_address", "attempted_at"),
        Index("idx_login_success_time", "success", "attempted_at"),
    )


class SecurityEvent(Base):
    """Security events and audit log"""

    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(SQLEnum(SecurityEventType), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    device_fingerprint = Column(String(255), nullable=True)
    location_country = Column(String(100), nullable=True)
    location_city = Column(String(100), nullable=True)
    metadata = Column(JSON, nullable=True)  # Additional event data
    risk_level = Column(String(20), default="low", nullable=False)  # low/medium/high
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="security_events")

    __table_args__ = (
        Index("idx_security_user_type", "user_id", "event_type"),
        Index("idx_security_type_time", "event_type", "created_at"),
        Index("idx_security_risk_time", "risk_level", "created_at"),
    )


class PasswordHistory(Base):
    """Password change history"""

    __tablename__ = "password_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    strength_score = Column(Integer, nullable=True)  # 0-100
    entropy = Column(Integer, nullable=True)
    changed_at = Column(DateTime, default=func.now(), nullable=False)
    changed_by_admin = Column(Boolean, default=False, nullable=False)
    change_reason = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="password_history")

    __table_args__ = (Index("idx_password_user_time", "user_id", "changed_at"),)


class DeviceToken(Base):
    """Device tokens for remember me functionality"""

    __tablename__ = "device_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    device_fingerprint = Column(String(255), nullable=False)
    device_name = Column(String(255), nullable=True)
    device_type = Column(SQLEnum(DeviceType), default=DeviceType.UNKNOWN)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="device_tokens")

    __table_args__ = (
        Index("idx_device_user_active", "user_id", "is_active"),
        Index("idx_device_fingerprint", "device_fingerprint"),
        Index("idx_device_expires", "expires_at"),
    )


class AccountLockout(Base):
    """Account lockout tracking"""

    __tablename__ = "account_lockouts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    lockout_reason = Column(String(255), nullable=False)
    failed_attempts = Column(Integer, default=0, nullable=False)
    locked_at = Column(DateTime, default=func.now(), nullable=False)
    unlocked_at = Column(DateTime, nullable=True)
    auto_unlock_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    user = relationship("User", back_populates="account_lockouts")

    __table_args__ = (
        Index("idx_lockout_email_active", "email", "is_active"),
        Index("idx_lockout_unlock_time", "auto_unlock_at"),
    )


# Update User model relationships (would be added to existing User model)
"""
Add these relationships to the existing User model in core/database.py:

    # Advanced Authentication relationships
    mfa_configurations = relationship(
        "MFAConfiguration", back_populates="user", cascade="all, delete-orphan"
    )
    social_accounts = relationship(
        "SocialAccount", back_populates="user", cascade="all, delete-orphan"
    )
    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )
    login_attempts = relationship(
        "LoginAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    security_events = relationship(
        "SecurityEvent", back_populates="user", cascade="all, delete-orphan"
    )
    password_history = relationship(
        "PasswordHistory", back_populates="user", cascade="all, delete-orphan"
    )
    device_tokens = relationship(
        "DeviceToken", back_populates="user", cascade="all, delete-orphan"
    )
    account_lockouts = relationship(
        "AccountLockout", back_populates="user", cascade="all, delete-orphan"
    )
"""
