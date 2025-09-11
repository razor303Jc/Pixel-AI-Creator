"""
Authentication middleware and dependencies for FastAPI.

This module provides:
- JWT authentication middleware
- Role-based access control decorators
- Dependency injection for protected routes
- User context management
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
from enum import Enum

from .jwt import verify_user_token


class UserRole(str, Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    CLIENT = "client"
    USER = "user"


# HTTP Bearer token security
security = HTTPBearer()


class AuthenticationMiddleware:
    """Authentication middleware for protecting routes."""

    def __init__(self):
        self.security = HTTPBearer()

    async def __call__(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Authenticate user from bearer token.

        Args:
            credentials: HTTP Bearer credentials

        Returns:
            User information from validated token

        Raises:
            HTTPException: If authentication fails
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = credentials.credentials
        user_info = verify_user_token(token)

        return user_info


class RoleChecker:
    """Role-based access control checker."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(
        self, user: Dict[str, Any] = Depends(AuthenticationMiddleware())
    ) -> Dict[str, Any]:
        """Check if user has required role.

        Args:
            user: User information from authentication

        Returns:
            User information if authorized

        Raises:
            HTTPException: If user doesn't have required role
        """
        user_role = user.get("role")

        if user_role not in [role.value for role in self.allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Insufficient permissions. Required roles: "
                    f"{[role.value for role in self.allowed_roles]}"
                ),
            )

        return user


# Global authentication dependency
authenticate_user = AuthenticationMiddleware()

# Role-based dependencies
require_admin = RoleChecker([UserRole.ADMIN])
require_client_or_admin = RoleChecker([UserRole.CLIENT, UserRole.ADMIN])
require_any_user = RoleChecker([UserRole.USER, UserRole.CLIENT, UserRole.ADMIN])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """Get current authenticated user.

    This is a simplified dependency for when you just need the user info
    without role checking.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Current user information
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    return verify_user_token(credentials.credentials)


def get_current_admin(
    user: Dict[str, Any] = Depends(authenticate_user),
) -> Dict[str, Any]:
    """Get current user if they are an admin.

    Args:
        user: Authenticated user

    Returns:
        User information if they are admin

    Raises:
        HTTPException: If user is not admin
    """
    if user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return user


def get_current_client(
    user: Dict[str, Any] = Depends(authenticate_user),
) -> Dict[str, Any]:
    """Get current user if they are a client or admin.

    Args:
        user: Authenticated user

    Returns:
        User information if they are client or admin

    Raises:
        HTTPException: If user doesn't have client access
    """
    user_role = user.get("role")
    if user_role not in [UserRole.CLIENT.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client or admin access required",
        )
    return user


class OwnershipChecker:
    """Check if user owns a resource or is admin."""

    def __init__(self, resource_field: str = "client_id"):
        self.resource_field = resource_field

    def check_ownership(self, user: Dict[str, Any], resource_owner_id: int) -> bool:
        """Check if user owns the resource or is admin.

        Args:
            user: Current user information
            resource_owner_id: ID of the resource owner

        Returns:
            True if user has access, False otherwise
        """
        # Admins can access everything
        if user.get("role") == UserRole.ADMIN.value:
            return True

        # Check if user owns the resource
        user_client_id = user.get("client_id")
        return user_client_id == resource_owner_id

    def __call__(
        self, resource_owner_id: int, user: Dict[str, Any] = Depends(authenticate_user)
    ) -> Dict[str, Any]:
        """Dependency to check resource ownership.

        Args:
            resource_owner_id: ID of the resource owner
            user: Current authenticated user

        Returns:
            User information if authorized

        Raises:
            HTTPException: If user doesn't own resource and isn't admin
        """
        if not self.check_ownership(user, resource_owner_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this resource",
            )

        return user


# Global ownership checker
check_ownership = OwnershipChecker()
