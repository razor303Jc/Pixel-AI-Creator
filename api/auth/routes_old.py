"""
Authentication routes for user registration, login, and management.

This module provides:
- User registration endpoint
- User login endpoint
- Password change endpoint
- User profile management
- Token refresh functionality
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
import logging

from ..core.database import get_db, User
from .models import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfile,
    UserRegistrationResponse,
    PasswordChangeRequest,
    UserUpdateRequest,
    SuccessResponse,
    UserRole
)
from .jwt import (
    create_user_token,
    hash_password,
    verify_password
)
from .middleware import (
    get_current_user
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def register_user(
    user_data: UserRegistrationRequest,
    db: AsyncSession = Depends(get_db)
) -> UserRegistrationResponse:
    """Register a new user account.
    
    Args:
        user_data: User registration information
        db: Database session
        
    Returns:
        User registration confirmation
        
    Raises:
        HTTPException: If email already exists or registration fails
    """
    try:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create new user
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            company_name=user_data.company_name,
            phone=user_data.phone,
            role=user_data.role.value,
            is_active=True
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return UserRegistrationResponse(
            message="User registered successfully",
            user_id=new_user.id,
            email=new_user.email,
            role=UserRole(new_user.role)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT token"
)
async def login_user(
    login_data: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Authenticate user and return JWT token.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        JWT token and user information
        
    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create token
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "client_id": user.id  # For ownership checks
        }
        
        access_token, expires_in = create_user_token(token_data)
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        await db.commit()
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=expires_in,
            user_id=user.id,
            role=UserRole(user.role)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get user profile",
    description="Get current user's profile information"
)
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserProfile:
    """Get current user's profile.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User profile information
        
    Raises:
        HTTPException: If user not found
    """
    try:
        result = await db.execute(
            select(User).where(User.id == current_user["user_id"])
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            company_name=user.company_name,
            phone=user.phone,
            role=UserRole(user.role),
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch profile"
        )


@router.put(
    "/profile",
    response_model=SuccessResponse,
    summary="Update user profile",
    description="Update current user's profile information"
)
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """Update current user's profile.
    
    Args:
        update_data: Profile update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success confirmation
        
    Raises:
        HTTPException: If user not found or update fails
    """
    try:
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields if provided
        if update_data.first_name is not None:
            user.first_name = update_data.first_name
        if update_data.last_name is not None:
            user.last_name = update_data.last_name
        if update_data.company_name is not None:
            user.company_name = update_data.company_name
        if update_data.phone is not None:
            user.phone = update_data.phone
        
        db.commit()
        
        logger.info(f"User profile updated: {user.email}")
        
        return SuccessResponse(
            message="Profile updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post(
    "/change-password",
    response_model=SuccessResponse,
    summary="Change password",
    description="Change current user's password"
)
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> SuccessResponse:
    """Change current user's password.
    
    Args:
        password_data: Current and new password
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success confirmation
        
    Raises:
        HTTPException: If current password is wrong or change fails
    """
    try:
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_password_hash = hash_password(password_data.new_password)
        user.password_hash = new_password_hash
        
        db.commit()
        
        logger.info(f"Password changed for user: {user.email}")
        
        return SuccessResponse(
            message="Password changed successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post(
    "/verify-token",
    response_model=UserProfile,
    summary="Verify JWT token",
    description="Verify token validity and return user information"
)
async def verify_token(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserProfile:
    """Verify JWT token and return user information.
    
    Args:
        current_user: Current authenticated user from token
        db: Database session
        
    Returns:
        User profile information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        user = db.query(User).filter(User.id == current_user["user_id"]).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        return UserProfile(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            company_name=user.company_name,
            phone=user.phone,
            role=UserRole(user.role),
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
