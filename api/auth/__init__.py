"""
Authentication package for Pixel AI Creator.

This package provides:
- JWT token handling
- Password security
- Authentication middleware
- User authentication routes
- Role-based access control
"""

from .jwt import (
    JWTHandler,
    PasswordHandler,
    create_user_token,
    verify_user_token,
    hash_password,
    verify_password,
)
from .middleware import (
    authenticate_user,
    get_current_user,
    get_current_admin,
    get_current_client,
    check_ownership,
    UserRole,
)
from .models import (
    UserRegistrationRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfile,
    UserRegistrationResponse,
    PasswordChangeRequest,
    UserUpdateRequest,
    SuccessResponse,
    ErrorResponse,
)
from .routes import router as auth_router

__all__ = [
    # JWT utilities
    "JWTHandler",
    "PasswordHandler",
    "create_user_token",
    "verify_user_token",
    "hash_password",
    "verify_password",
    # Middleware
    "authenticate_user",
    "get_current_user",
    "get_current_admin",
    "get_current_client",
    "check_ownership",
    "UserRole",
    # Models
    "UserRegistrationRequest",
    "UserLoginRequest",
    "TokenResponse",
    "UserProfile",
    "UserRegistrationResponse",
    "PasswordChangeRequest",
    "UserUpdateRequest",
    "SuccessResponse",
    "ErrorResponse",
    # Router
    "auth_router",
]
