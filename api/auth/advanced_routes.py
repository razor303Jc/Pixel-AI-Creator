"""
Advanced Authentication Routes
Enhanced authentication endpoints including MFA, social login, and password policies.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, List
import logging
from datetime import datetime

from core.database import get_db, User
from .models import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfile,
    SuccessResponse,
    UserRole,
)
from .advanced_models import (
    MFASetupRequest,
    MFASetupResponse,
    MFAVerificationRequest,
    MFAStatusResponse,
    SocialLoginRequest,
    SocialLoginResponse,
    PasswordStrengthResponse,
    PasswordChangeAdvancedRequest,
    EnhancedTokenResponse,
    SecurityDashboardResponse,
    DeviceInfo,
    DeviceType,
    LoginAttemptStatus,
    SocialProvider,
    MFAMethod,
)
from .jwt import create_user_token, hash_password, verify_password
from .middleware import get_current_user
from .mfa_service import mfa_service
from .password_service import password_policy_service
from .social_service import social_login_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth/advanced", tags=["Advanced Authentication"])


def get_device_info(request: Request) -> DeviceInfo:
    """Extract device information from request"""
    user_agent = request.headers.get("user-agent", "")
    client_ip = request.client.host if request.client else "unknown"

    # Simple device type detection
    device_type = DeviceType.UNKNOWN
    if "mobile" in user_agent.lower():
        device_type = DeviceType.MOBILE
    elif "tablet" in user_agent.lower():
        device_type = DeviceType.TABLET
    else:
        device_type = DeviceType.DESKTOP

    return DeviceInfo(
        device_type=device_type,
        browser=user_agent.split("/")[0] if "/" in user_agent else "unknown",
        os="unknown",  # Would need more sophisticated parsing
        ip_address=client_ip,
        user_agent=user_agent,
    )


# === MFA ENDPOINTS ===


@router.post(
    "/mfa/setup",
    response_model=MFASetupResponse,
    summary="Set up Multi-Factor Authentication",
    description="Initialize MFA setup for the current user",
)
async def setup_mfa(
    mfa_request: MFASetupRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MFASetupResponse:
    """Set up MFA for the current user"""
    try:
        user_id = current_user["user_id"]
        email = current_user["email"]

        if mfa_request.method == MFAMethod.TOTP:
            response = await mfa_service.setup_totp_mfa(user_id, email, db)
            logger.info(f"TOTP MFA setup initiated for user {user_id}")
            return response

        elif mfa_request.method == MFAMethod.SMS:
            if not mfa_request.phone_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number is required for SMS MFA",
                )

            # Generate and send SMS code
            sms_code = mfa_service.generate_sms_code()
            success = await mfa_service.send_sms_code(
                mfa_request.phone_number, sms_code
            )

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send SMS verification code",
                )

            return MFASetupResponse(
                method=MFAMethod.SMS,
                phone_number=f"***-***-{mfa_request.phone_number[-4:]}",
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"MFA method {mfa_request.method} not implemented",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set up MFA",
        )


@router.post(
    "/mfa/verify",
    response_model=SuccessResponse,
    summary="Verify MFA code",
    description="Verify MFA verification code",
)
async def verify_mfa(
    mfa_verification: MFAVerificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """Verify MFA code for the current user"""
    try:
        user_id = current_user["user_id"]

        is_valid = await mfa_service.verify_mfa_code(
            user_id, mfa_verification.method, mfa_verification.code, db
        )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code"
            )

        logger.info(f"MFA verification successful for user {user_id}")
        return SuccessResponse(message="MFA code verified successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MFA: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify MFA code",
        )


@router.get(
    "/mfa/status",
    response_model=MFAStatusResponse,
    summary="Get MFA status",
    description="Get current MFA configuration status",
)
async def get_mfa_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    """Get MFA status for the current user"""
    try:
        user_id = current_user["user_id"]
        status_info = await mfa_service.get_mfa_status(user_id, db)
        return status_info

    except Exception as e:
        logger.error(f"Error getting MFA status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MFA status",
        )


# === PASSWORD STRENGTH ENDPOINTS ===


@router.post(
    "/password/check-strength",
    response_model=PasswordStrengthResponse,
    summary="Check password strength",
    description="Analyze password strength and policy compliance",
)
async def check_password_strength(
    password_data: Dict[str, str],
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> PasswordStrengthResponse:
    """Check password strength and policy compliance"""
    try:
        password = password_data.get("password", "")
        if not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Password is required"
            )

        # Get user info for personal data checking
        user_info = {
            "first_name": current_user.get("first_name", ""),
            "last_name": current_user.get("last_name", ""),
            "email": current_user.get("email", ""),
            "company_name": current_user.get("company_name", ""),
        }

        analysis = password_policy_service.analyze_password_strength(
            password, user_info=user_info
        )

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking password strength: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check password strength",
        )


@router.post(
    "/password/change-advanced",
    response_model=SuccessResponse,
    summary="Advanced password change",
    description="Change password with MFA verification",
)
async def change_password_advanced(
    password_data: PasswordChangeAdvancedRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SuccessResponse:
    """Change password with enhanced security checks"""
    try:
        user_id = current_user["user_id"]

        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        # Check if MFA is required and verify if provided
        mfa_status = await mfa_service.get_mfa_status(user_id, db)
        if mfa_status.enabled and not password_data.mfa_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA code is required"
            )

        if mfa_status.enabled and password_data.mfa_code:
            mfa_valid = await mfa_service.verify_mfa_code(
                user_id,
                MFAMethod.TOTP,  # Assume TOTP for now
                password_data.mfa_code,
                db,
            )
            if not mfa_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid MFA code"
                )

        # Validate new password strength
        user_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "company_name": user.company_name,
        }

        if not password_policy_service.validate_password(
            password_data.new_password, user_info=user_info
        ):
            analysis = password_policy_service.analyze_password_strength(
                password_data.new_password, user_info=user_info
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password does not meet policy requirements: {', '.join(analysis.feedback)}",
            )

        # Update password
        new_password_hash = hash_password(password_data.new_password)
        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Advanced password change successful for user {user_id}")
        return SuccessResponse(message="Password changed successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )


# === SOCIAL LOGIN ENDPOINTS ===


@router.get(
    "/social/providers",
    summary="Get available social providers",
    description="Get list of available social login providers",
)
async def get_social_providers() -> Dict[str, List[str]]:
    """Get available social login providers"""
    return {
        "providers": [provider.value for provider in SocialProvider],
        "enabled": ["google", "github"],  # Would come from configuration
    }


@router.get(
    "/social/{provider}/authorize",
    summary="Get social login authorization URL",
    description="Get OAuth authorization URL for social provider",
)
async def get_social_auth_url(
    provider: SocialProvider, redirect_uri: str, state: str = "default"
) -> Dict[str, str]:
    """Get social login authorization URL"""
    try:
        auth_url = social_login_service.get_authorization_url(
            provider, redirect_uri, state
        )

        return {
            "authorization_url": auth_url,
            "provider": provider.value,
            "state": state,
        }

    except Exception as e:
        logger.error(f"Error generating auth URL for {provider}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL for {provider}",
        )


@router.post(
    "/social/login",
    response_model=SocialLoginResponse,
    summary="Social login",
    description="Authenticate user via social provider",
)
async def social_login(
    login_request: SocialLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SocialLoginResponse:
    """Authenticate user via social provider"""
    try:
        # Get user info from social provider
        user_data = await social_login_service.get_user_info_from_token(
            login_request.provider, login_request.access_token
        )

        if not user_data.get("email"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by social provider",
            )

        email = user_data["email"]

        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        is_new_user = False

        if not user:
            # Create new user
            is_new_user = True
            user = User(
                email=email,
                password_hash="",  # No password for social login
                first_name=user_data.get("first_name", ""),
                last_name=user_data.get("last_name", ""),
                role=UserRole.USER.value,
                is_active=True,
                is_verified=True,  # Social accounts are pre-verified
            )

            db.add(user)
            await db.commit()
            await db.refresh(user)

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Create tokens
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "client_id": user.id,
        }

        access_token, expires_in = create_user_token(token_data)

        logger.info(f"Social login successful for {email} via {login_request.provider}")

        return SocialLoginResponse(
            access_token=access_token,
            refresh_token=access_token,  # Would implement refresh tokens
            token_type="bearer",
            expires_in=expires_in,
            user_id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            avatar_url=user_data.get("avatar_url"),
            is_new_user=is_new_user,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in social login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Social login failed",
        )


# === ENHANCED LOGIN ===


@router.post(
    "/login-enhanced",
    response_model=EnhancedTokenResponse,
    summary="Enhanced login with security features",
    description="Login with device tracking and security monitoring",
)
async def enhanced_login(
    login_data: UserLoginRequest, request: Request, db: AsyncSession = Depends(get_db)
) -> EnhancedTokenResponse:
    """Enhanced login with security features"""
    try:
        device_info = get_device_info(request)

        # Find user
        result = await db.execute(select(User).where(User.email == login_data.email))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Check MFA status
        mfa_status = await mfa_service.get_mfa_status(user.id, db)

        # Create tokens
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "client_id": user.id,
        }

        access_token, expires_in = create_user_token(token_data)

        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()

        # Calculate security score (simplified)
        security_score = 70  # Base score
        if mfa_status.enabled:
            security_score += 20
        if user.password_hash:  # Has strong password
            security_score += 10

        logger.info(f"Enhanced login successful for {user.email}")

        return EnhancedTokenResponse(
            access_token=access_token,
            refresh_token=access_token,  # Would implement refresh tokens
            token_type="bearer",
            expires_in=expires_in,
            user_id=user.id,
            email=user.email,
            role=user.role,
            mfa_enabled=mfa_status.enabled,
            mfa_required=False,  # Would check if MFA is required for this login
            session_id="session_" + str(user.id),  # Would generate proper session ID
            device_fingerprint=device_info.user_agent[:50],
            last_login=user.last_login,
            security_score=security_score,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Enhanced login failed",
        )


# === SECURITY DASHBOARD ===


@router.get(
    "/security/dashboard",
    response_model=SecurityDashboardResponse,
    summary="Get security dashboard",
    description="Get comprehensive security information for the user",
)
async def get_security_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SecurityDashboardResponse:
    """Get security dashboard information"""
    try:
        user_id = current_user["user_id"]

        # Get MFA status
        mfa_status = await mfa_service.get_mfa_status(user_id, db)

        # For demo purposes, return mock data
        # In production, would query database for actual data

        return SecurityDashboardResponse(
            mfa_status=mfa_status,
            recent_logins=[],  # Would query login attempts
            active_sessions=[],  # Would query active sessions
            security_events=[],  # Would query security events
            linked_accounts=[],  # Would query linked social accounts
            password_last_changed=datetime.utcnow(),  # Would get from user record
            account_security_score=85,  # Would calculate based on security factors
        )

    except Exception as e:
        logger.error(f"Error getting security dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get security dashboard",
        )
