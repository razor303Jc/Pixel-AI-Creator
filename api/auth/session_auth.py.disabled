"""
Enhanced authentication routes with session management.

This module provides:
- Session-aware login/logout
- Session tracking
- Device management
- Security monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from core.database import get_db
from auth.jwt import JWTHandler, PasswordHandler
from auth.models import UserLoginRequest, TokenResponse, UserRegistrationRequest
from auth.session_models import SessionCreateRequest, SessionResponse
from services.session_service import SessionManager
from models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])

jwt_handler = JWTHandler()
password_handler = PasswordHandler()


@router.post("/login", response_model=TokenResponse)
async def login_with_session(
    login_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)
):
    """Enhanced login with session management."""

    try:
        # Authenticate user
        user = db.query(User).filter(User.email == login_data.email).first()

        if not user or not password_handler.verify_password(
            login_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated",
            )

        # Get request information for session
        client_ip = request.client.host
        user_agent = request.headers.get("user-agent", "")

        # Create session
        session_manager = SessionManager(db)

        # Create refresh token first
        refresh_token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
        }
        refresh_token = jwt_handler.create_refresh_token(refresh_token_data)

        # Create session request
        session_request = SessionCreateRequest(
            device_type="unknown",  # Could be enhanced with user agent parsing
            user_agent=user_agent,
            ip_address=client_ip,
        )

        # Create session
        session = session_manager.create_session(
            user_id=user.id,
            refresh_token=refresh_token,
            request_data=session_request,
            ip_address=client_ip,
            user_agent=user_agent,
        )

        # Create access token with session ID
        access_token_data = {"user_id": user.id, "email": user.email, "role": user.role}
        access_token = jwt_handler.create_access_token(
            access_token_data, session_id=session.id
        )

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=jwt_handler.access_token_expire_minutes * 60,
            user_id=user.id,
            role=user.role,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed"
        )


@router.post("/logout")
async def logout_with_session(request: Request, db: Session = Depends(get_db)):
    """Enhanced logout with session termination."""

    try:
        # Get token from header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid token provided",
            )

        token = auth_header.split(" ")[1]

        # Verify token and get session ID
        try:
            payload = jwt_handler.verify_token(token)
            session_id = payload.get("session_id")

            if session_id:
                session_manager = SessionManager(db)
                session_manager.terminate_session(session_id, "user_logout")

        except Exception:
            # Token might be invalid, but that's okay for logout
            pass

        return {"message": "Logged out successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return {"message": "Logged out successfully"}  # Always succeed for logout


@router.post("/logout-all")
async def logout_all_sessions(request: Request, db: Session = Depends(get_db)):
    """Logout from all sessions."""

    try:
        # Get token from header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No valid token provided",
            )

        token = auth_header.split(" ")[1]

        # Verify token and get user ID
        try:
            payload = jwt_handler.verify_token(token)
            user_id = payload.get("user_id")
            current_session_id = payload.get("session_id")

            if user_id:
                session_manager = SessionManager(db)
                terminated_count = session_manager.terminate_user_sessions(
                    user_id=user_id,
                    exclude_session_id=None,  # Terminate all sessions
                    reason="logout_all",
                )

                return {
                    "message": f"Logged out from {terminated_count} sessions",
                    "terminated_count": terminated_count,
                }

        except Exception as e:
            logger.error(f"Error terminating sessions: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        return {"message": "No active sessions found"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout all error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout from all sessions",
        )


@router.post("/refresh")
async def refresh_token(request: Request, db: Session = Depends(get_db)):
    """Refresh access token using session."""

    try:
        # Get refresh token from request body or header
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No refresh token provided",
            )

        refresh_token = auth_header.split(" ")[1]

        # Find session with this refresh token
        session_manager = SessionManager(db)
        session = (
            db.query(session_manager.UserSession)
            .filter(session_manager.UserSession.refresh_token == refresh_token)
            .first()
        )

        if not session or not session.is_active():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        # Get user
        user = db.query(User).filter(User.id == session.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Refresh session
        refreshed_session = session_manager.refresh_session(session.id)
        if not refreshed_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh session",
            )

        # Create new access token
        access_token_data = {"user_id": user.id, "email": user.email, "role": user.role}
        access_token = jwt_handler.create_access_token(
            access_token_data, session_id=session.id
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": jwt_handler.access_token_expire_minutes * 60,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token",
        )
