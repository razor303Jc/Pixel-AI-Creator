"""
Enhanced Authentication Routes

This module provides advanced authentication endpoints including:
- Multi-factor authentication (MFA/2FA)
- Social login integration
- Password strength validation
- Device tracking and session management
- Advanced security features
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import user_agents
from pydantic import BaseModel, EmailStr, validator

from models.database_schema import User
from auth.advanced_models import (
    MFAMethod,
    SocialProvider,
    DeviceInfo,
)
from auth.advanced_database_models import (
    LoginAttempt,
    MFAConfiguration as UserMFA,
    SocialAccount,
    PasswordHistory,
)
from auth.middleware import get_current_user
from core.database import get_db
from auth.jwt import jwt_handler, hash_password, verify_password
from services.mfa_service import mfa_service
from services.password_strength_service import password_strength_service
from services.social_login_service import social_login_service
from core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/advanced", tags=["Enhanced Authentication"])
security = HTTPBearer()


# Request/Response Models
class MFASetupRequest(BaseModel):
    method: MFAMethod = MFAMethod.TOTP


class MFASetupResponse(BaseModel):
    secret_key: str
    qr_code_url: str
    backup_codes: List[str]
    setup_complete: bool = False


class MFAVerificationRequest(BaseModel):
    code: str
    remember_device: bool = False


class MFALoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None
    device_name: Optional[str] = None
    remember_device: bool = False


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @validator("new_password")
    def validate_password_strength(cls, v):
        analysis = password_strength_service.analyze_password_strength(v)
        if not analysis["is_valid"]:
            raise ValueError(
                f"Password does not meet requirements: {', '.join(analysis['suggestions'])}"
            )
        return v


class PasswordStrengthRequest(BaseModel):
    password: str
    user_inputs: Optional[List[str]] = []


class SocialLoginResponse(BaseModel):
    authorization_url: str
    state: str
    provider: str


class DeviceInfoResponse(BaseModel):
    id: int
    device_name: str
    device_type: str
    browser: str
    os: str
    is_current: bool
    is_trusted: bool
    last_used: datetime
    created_at: datetime


class LoginAttemptResponse(BaseModel):
    id: int
    ip_address: str
    user_agent: str
    success: bool
    failure_reason: Optional[str]
    location: Optional[str]
    device_info: Optional[str]
    attempted_at: datetime


# Utility Functions
def extract_device_info(request: Request) -> Dict[str, Any]:
    """Extract device information from request"""
    user_agent = request.headers.get("user-agent", "")
    ua = user_agents.parse(user_agent)

    return {
        "user_agent": user_agent,
        "browser": f"{ua.browser.family} {ua.browser.version_string}",
        "os": f"{ua.os.family} {ua.os.version_string}",
        "device_family": ua.device.family,
        "is_mobile": ua.is_mobile,
        "is_tablet": ua.is_tablet,
        "is_pc": ua.is_pc,
        "is_bot": ua.is_bot,
    }


def get_client_ip(request: Request) -> str:
    """Get client IP address with proxy support"""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


async def log_login_attempt(
    db: AsyncSession,
    email: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    failure_reason: Optional[str] = None,
    user_id: Optional[int] = None,
):
    """Log login attempt for security monitoring"""
    try:
        device_info = extract_device_info(
            type("Request", (), {"headers": {"user-agent": user_agent}})()
        )

        login_attempt = LoginAttempt(
            user_id=user_id,
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason,
            device_info=device_info,
        )

        db.add(login_attempt)
        await db.commit()

    except Exception as e:
        logger.error(f"Failed to log login attempt: {e}")


# MFA Endpoints
@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: MFASetupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Setup multi-factor authentication for user"""
    try:
        # Check if MFA is already enabled
        existing_mfa = await db.execute(
            select(UserMFA).where(
                and_(UserMFA.user_id == current_user.id, UserMFA.is_active == True)
            )
        )

        if existing_mfa.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled for this account",
            )

        # Setup MFA
        setup_data = await mfa_service.setup_mfa_for_user(
            current_user.id, request.method, db
        )

        return MFASetupResponse(**setup_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA setup failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="MFA setup failed"
        )


@router.post("/mfa/verify-setup")
async def verify_mfa_setup(
    request: MFAVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Verify MFA setup with TOTP code"""
    try:
        success = await mfa_service.verify_mfa_setup(current_user.id, request.code, db)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        return {"message": "MFA setup completed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA verification failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MFA verification failed",
        )


@router.post("/mfa/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Disable MFA for user account"""
    try:
        success = await mfa_service.disable_mfa(current_user.id, db)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA not found or already disabled",
            )

        return {"message": "MFA disabled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MFA disable failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA",
        )


@router.get("/mfa/backup-codes")
async def get_backup_codes(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get backup codes for MFA"""
    try:
        backup_codes = await mfa_service.get_backup_codes(current_user.id, db)

        return {"backup_codes": backup_codes}

    except Exception as e:
        logger.error(f"Failed to get backup codes for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve backup codes",
        )


@router.post("/mfa/regenerate-backup-codes")
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Regenerate backup codes for MFA"""
    try:
        new_codes = await mfa_service.regenerate_backup_codes(current_user.id, db)

        return {"backup_codes": new_codes}

    except Exception as e:
        logger.error(
            f"Failed to regenerate backup codes for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes",
        )


# Enhanced Authentication
@router.post("/login-mfa")
async def login_with_mfa(
    request: MFALoginRequest, http_request: Request, db: AsyncSession = Depends(get_db)
):
    """Enhanced login with MFA support"""
    ip_address = get_client_ip(http_request)
    user_agent = http_request.headers.get("user-agent", "")
    device_info = extract_device_info(http_request)

    try:
        # Find user
        result = await db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(request.password, user.password_hash):
            await log_login_attempt(
                db, request.email, ip_address, user_agent, False, "Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Check if MFA is enabled
        mfa_result = await db.execute(
            select(UserMFA).where(
                and_(UserMFA.user_id == user.id, UserMFA.is_active == True)
            )
        )
        user_mfa = mfa_result.scalar_one_or_none()

        if user_mfa:
            if not request.mfa_code:
                # MFA required but code not provided
                return {"mfa_required": True, "message": "MFA verification required"}

            # Verify MFA code
            mfa_valid = await mfa_service.verify_mfa_login(
                user.id, request.mfa_code, db
            )

            if not mfa_valid:
                await log_login_attempt(
                    db,
                    request.email,
                    ip_address,
                    user_agent,
                    False,
                    "Invalid MFA code",
                    user.id,
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
                )

        # Create access token
        access_token = jwt_handler.create_access_token(data={"sub": str(user.id)})

        # Update last login
        user.last_login = datetime.utcnow()

        # Create or update device info
        if request.device_name:
            device = DeviceInfo(
                user_id=user.id,
                device_name=request.device_name,
                device_type=device_info.get("device_family", "Unknown"),
                browser=device_info.get("browser", "Unknown"),
                os=device_info.get("os", "Unknown"),
                ip_address=ip_address,
                user_agent=user_agent,
                is_trusted=request.remember_device,
                last_used=datetime.utcnow(),
            )
            db.add(device)

        await db.commit()

        # Log successful login
        await log_login_attempt(
            db, request.email, ip_address, user_agent, True, None, user.id
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "mfa_enabled": user_mfa is not None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed for {request.email}: {e}")
        await log_login_attempt(
            db, request.email, ip_address, user_agent, False, "Internal error"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


# Password Management
@router.post("/password/change")
async def change_password(
    request: PasswordChangeRequest,
    http_request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password with strength validation"""
    try:
        # Verify current password
        if not verify_password(request.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Check password history
        history_valid = await password_strength_service.validate_password_history(
            current_user.id, request.new_password, db
        )

        if not history_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password was recently used. Please choose a different password.",
            )

        # Hash new password
        new_password_hash = hash_password(request.new_password)

        # Update password
        current_user.password_hash = new_password_hash
        current_user.password_changed_at = datetime.utcnow()

        # Add to password history
        ip_address = get_client_ip(http_request)
        user_agent = http_request.headers.get("user-agent", "")

        await password_strength_service.add_to_password_history(
            current_user.id, new_password_hash, db, ip_address, user_agent, True
        )

        await db.commit()

        return {"message": "Password changed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )


@router.post("/password/strength-check")
async def check_password_strength(
    request: PasswordStrengthRequest, current_user: User = Depends(get_current_user)
):
    """Check password strength and provide feedback"""
    try:
        # Include user-specific data for analysis
        user_inputs = request.user_inputs or []
        user_inputs.extend(
            [
                current_user.email,
                current_user.first_name or "",
                current_user.last_name or "",
            ]
        )

        analysis = password_strength_service.analyze_password_strength(
            request.password, user_inputs
        )

        return {
            "score": analysis["score"],
            "is_valid": analysis["is_valid"],
            "feedback": analysis["feedback"],
            "suggestions": analysis["suggestions"],
            "warnings": analysis["warnings"],
            "estimated_crack_time": analysis["estimated_crack_time"],
        }

    except Exception as e:
        logger.error(f"Password strength check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze password strength",
        )


# Social Login Endpoints
@router.get("/social/authorize/{provider}")
async def social_authorize(provider: SocialProvider, request: Request):
    """Start social login authorization flow"""
    try:
        # Build redirect URI
        redirect_uri = (
            f"{settings.BASE_URL}/auth/advanced/social/callback/{provider.value}"
        )

        auth_data = social_login_service.get_authorization_url(provider, redirect_uri)

        return SocialLoginResponse(**auth_data)

    except Exception as e:
        logger.error(f"Social authorization failed for {provider.value}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate social login",
        )


@router.get("/social/callback/{provider}")
async def social_callback(
    provider: SocialProvider, code: str, state: str, db: AsyncSession = Depends(get_db)
):
    """Handle social login callback"""
    try:
        callback_data = await social_login_service.handle_oauth_callback(
            provider, code, state, db
        )

        social_login = callback_data["social_login"]

        if social_login.user_id:
            # Existing user login
            access_token = jwt_handler.create_access_token(
                data={"sub": str(social_login.user_id)}
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": social_login.user_id,
                "provider": provider.value,
            }
        else:
            # New user registration required
            return {
                "registration_required": True,
                "social_login_id": social_login.id,
                "user_info": callback_data["user_info"],
                "provider": provider.value,
            }

    except Exception as e:
        logger.error(f"Social callback failed for {provider.value}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Social login callback failed",
        )


@router.get("/social/accounts")
async def get_social_accounts(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's linked social accounts"""
    try:
        accounts = await social_login_service.get_user_social_accounts(
            current_user.id, db
        )

        return {"social_accounts": accounts}

    except Exception as e:
        logger.error(f"Failed to get social accounts for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve social accounts",
        )


@router.delete("/social/unlink/{provider}")
async def unlink_social_account(
    provider: SocialProvider,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Unlink social account from user"""
    try:
        success = await social_login_service.unlink_social_account(
            current_user.id, provider, db
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Social account not found"
            )

        return {"message": f"{provider.value} account unlinked successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to unlink {provider.value} for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink social account",
        )


# Security & Device Management
@router.get("/devices", response_model=List[DeviceInfoResponse])
async def get_user_devices(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get user's registered devices"""
    try:
        result = await db.execute(
            select(DeviceInfo)
            .where(DeviceInfo.user_id == current_user.id)
            .order_by(DeviceInfo.last_used.desc())
        )

        devices = result.scalars().all()

        return [
            DeviceInfoResponse(
                id=device.id,
                device_name=device.device_name,
                device_type=device.device_type,
                browser=device.browser,
                os=device.os,
                is_current=False,  # TODO: Determine current device
                is_trusted=device.is_trusted,
                last_used=device.last_used,
                created_at=device.created_at,
            )
            for device in devices
        ]

    except Exception as e:
        logger.error(f"Failed to get devices for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve devices",
        )


@router.delete("/devices/{device_id}")
async def remove_device(
    device_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a registered device"""
    try:
        result = await db.execute(
            select(DeviceInfo).where(
                and_(DeviceInfo.id == device_id, DeviceInfo.user_id == current_user.id)
            )
        )

        device = result.scalar_one_or_none()
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Device not found"
            )

        await db.delete(device)
        await db.commit()

        return {"message": "Device removed successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to remove device {device_id} for user {current_user.id}: {e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove device",
        )


@router.get("/login-history", response_model=List[LoginAttemptResponse])
async def get_login_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's login history"""
    try:
        result = await db.execute(
            select(LoginAttempt)
            .where(LoginAttempt.user_id == current_user.id)
            .order_by(LoginAttempt.attempted_at.desc())
            .limit(limit)
        )

        attempts = result.scalars().all()

        return [
            LoginAttemptResponse(
                id=attempt.id,
                ip_address=attempt.ip_address,
                user_agent=attempt.user_agent,
                success=attempt.success,
                failure_reason=attempt.failure_reason,
                location=attempt.location,
                device_info=str(attempt.device_info) if attempt.device_info else None,
                attempted_at=attempt.attempted_at,
            )
            for attempt in attempts
        ]

    except Exception as e:
        logger.error(f"Failed to get login history for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve login history",
        )
