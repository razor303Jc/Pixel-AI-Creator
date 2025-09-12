"""
Advanced Authentication Models
Enhanced authentication features including MFA, social login, and security models.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import re


class MFAMethod(str, Enum):
    """Multi-factor authentication methods"""

    TOTP = "totp"  # Time-based One-Time Password (Google Authenticator, Authy)
    SMS = "sms"  # SMS-based verification
    EMAIL = "email"  # Email-based verification
    BACKUP_CODES = "backup_codes"  # Recovery backup codes


class SocialProvider(str, Enum):
    """Social login providers"""

    GOOGLE = "google"
    GITHUB = "github"
    LINKEDIN = "linkedin"
    MICROSOFT = "microsoft"


class LoginAttemptStatus(str, Enum):
    """Login attempt status"""

    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    MFA_REQUIRED = "mfa_required"


class DeviceType(str, Enum):
    """Device types for tracking"""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    API = "api"
    UNKNOWN = "unknown"


# === MFA MODELS ===


class MFASetupRequest(BaseModel):
    """Request to set up MFA for a user"""

    method: MFAMethod
    phone_number: Optional[str] = Field(None, description="Required for SMS MFA")

    @validator("phone_number")
    def validate_phone_for_sms(cls, v, values):
        if values.get("method") == MFAMethod.SMS and not v:
            raise ValueError("Phone number is required for SMS MFA")
        return v


class MFASetupResponse(BaseModel):
    """Response containing MFA setup information"""

    method: MFAMethod
    secret: Optional[str] = Field(
        None, description="TOTP secret for QR code generation"
    )
    qr_code_url: Optional[str] = Field(None, description="QR code URL for TOTP setup")
    backup_codes: Optional[List[str]] = Field(None, description="Recovery backup codes")
    phone_number: Optional[str] = Field(None, description="Masked phone number for SMS")


class MFAVerificationRequest(BaseModel):
    """Request to verify MFA code"""

    method: MFAMethod
    code: str = Field(
        ..., min_length=6, max_length=8, description="MFA verification code"
    )
    backup_code: Optional[str] = Field(None, description="Backup recovery code")


class MFAStatusResponse(BaseModel):
    """MFA status for a user"""

    enabled: bool
    methods: List[MFAMethod]
    backup_codes_remaining: int
    last_used: Optional[datetime]


# === SOCIAL LOGIN MODELS ===


class SocialLoginRequest(BaseModel):
    """Social login request"""

    provider: SocialProvider
    access_token: str = Field(..., description="OAuth access token from provider")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI after login")


class SocialLoginResponse(BaseModel):
    """Social login response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str
    first_name: str
    last_name: str
    avatar_url: Optional[str]
    is_new_user: bool


class SocialAccountLink(BaseModel):
    """Social account linking information"""

    provider: SocialProvider
    provider_id: str
    email: str
    profile_url: Optional[str]
    avatar_url: Optional[str]
    linked_at: datetime


# === PASSWORD POLICY MODELS ===


class PasswordPolicy(BaseModel):
    """Password strength policy configuration"""

    min_length: int = Field(8, ge=6, le=128)
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_numbers: bool = True
    require_special_chars: bool = True
    min_special_chars: int = Field(1, ge=0, le=5)
    max_length: int = Field(128, ge=8, le=256)
    prevent_common_passwords: bool = True
    prevent_personal_info: bool = True


class PasswordStrengthResponse(BaseModel):
    """Password strength analysis response"""

    score: int = Field(..., ge=0, le=100, description="Password strength score (0-100)")
    strength: str = Field(..., description="Strength level: weak, fair, good, strong")
    feedback: List[str] = Field(..., description="List of improvement suggestions")
    meets_policy: bool = Field(
        ..., description="Whether password meets policy requirements"
    )
    estimated_crack_time: str = Field(
        ..., description="Estimated time to crack password"
    )


class PasswordChangeAdvancedRequest(BaseModel):
    """Advanced password change with verification"""

    current_password: str
    new_password: str
    mfa_code: Optional[str] = Field(None, description="MFA code if MFA is enabled")

    @validator("new_password")
    def validate_password_strength(cls, v):
        """Basic password validation"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Password must contain at least one special character")

        return v


# === DEVICE & SECURITY MODELS ===


class DeviceInfo(BaseModel):
    """Device information for tracking"""

    device_type: DeviceType
    browser: Optional[str]
    os: Optional[str]
    ip_address: str
    user_agent: str
    location: Optional[Dict[str, Any]] = Field(None, description="Geolocation data")


class LoginAttempt(BaseModel):
    """Login attempt tracking"""

    email: str
    status: LoginAttemptStatus
    ip_address: str
    user_agent: str
    device_info: DeviceInfo
    timestamp: datetime
    failure_reason: Optional[str]
    mfa_used: Optional[MFAMethod]


class SecurityEvent(BaseModel):
    """Security event tracking"""

    user_id: Optional[int]
    event_type: str
    severity: str  # low, medium, high, critical
    description: str
    ip_address: str
    user_agent: str
    metadata: Optional[Dict[str, Any]]
    timestamp: datetime


class LoginSessionInfo(BaseModel):
    """Enhanced login session information"""

    session_id: str
    user_id: int
    device_info: DeviceInfo
    login_time: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool
    mfa_verified: bool


# === ENHANCED AUTH RESPONSES ===


class EnhancedTokenResponse(BaseModel):
    """Enhanced token response with security info"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    email: str
    role: str
    mfa_enabled: bool
    mfa_required: bool = False
    session_id: str
    device_fingerprint: str
    last_login: Optional[datetime]
    security_score: int = Field(..., ge=0, le=100, description="Account security score")


class SecurityDashboardResponse(BaseModel):
    """Security dashboard information"""

    mfa_status: MFAStatusResponse
    recent_logins: List[LoginAttempt]
    active_sessions: List[LoginSessionInfo]
    security_events: List[SecurityEvent]
    linked_accounts: List[SocialAccountLink]
    password_last_changed: Optional[datetime]
    account_security_score: int


# === ADMIN MODELS ===


class UserSecurityReport(BaseModel):
    """Admin view of user security status"""

    user_id: int
    email: str
    mfa_enabled: bool
    failed_login_attempts: int
    last_successful_login: Optional[datetime]
    account_locked: bool
    security_events_count: int
    linked_social_accounts: int
    password_age_days: int
    security_score: int


class SecurityPolicyConfig(BaseModel):
    """System-wide security policy configuration"""

    password_policy: PasswordPolicy
    max_failed_attempts: int = Field(5, ge=1, le=20)
    lockout_duration_minutes: int = Field(30, ge=5, le=1440)
    session_timeout_minutes: int = Field(60, ge=15, le=1440)
    require_mfa_for_admin: bool = True
    allow_social_login: bool = True
    enabled_social_providers: List[SocialProvider]
    enable_device_tracking: bool = True
    enable_geolocation: bool = False
