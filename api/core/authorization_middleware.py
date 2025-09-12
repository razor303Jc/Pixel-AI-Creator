"""
Authorization Middleware

This middleware provides comprehensive authorization functionality for FastAPI applications:
- Automatic permission checking for protected endpoints
- Role-based access control enforcement
- Resource-specific permission validation
- Audit logging for authorization events
- Multi-tenant organization support
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
import json

from core.database import get_db_session
from core.auth import get_current_user_from_token
from models.database_schema import User
from services.authorization_service import authorization_service

logger = logging.getLogger(__name__)


class AuthorizationMiddleware(BaseHTTPMiddleware):
    """
    Authorization middleware that automatically enforces permissions
    """

    def __init__(
        self,
        app,
        excluded_paths: List[str] = None,
        permission_map: Dict[str, Dict[str, str]] = None,
    ):
        super().__init__(app)

        # Paths that don't require authorization
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/health",
            "/favicon.ico",
        ]

        # Default permission mapping for HTTP methods and paths
        self.permission_map = permission_map or {
            # System permissions
            "/api/v1/auth/permissions": {
                "GET": "system.read",
                "POST": "system.manage",
                "PUT": "system.manage",
                "DELETE": "system.manage",
            },
            "/api/v1/auth/roles": {
                "GET": "system.read",
                "POST": "system.manage",
                "PUT": "system.manage",
                "DELETE": "system.manage",
            },
            "/api/v1/auth/audit": {"GET": "system.read"},
            # User management
            "/api/v1/users": {
                "GET": "user.read",
                "POST": "user.create",
                "PUT": "user.update",
                "DELETE": "user.delete",
            },
            # Client management
            "/api/v1/clients": {
                "GET": "client.read",
                "POST": "client.create",
                "PUT": "client.update",
                "DELETE": "client.delete",
            },
            # Chatbot management
            "/api/v1/chatbots": {
                "GET": "chatbot.read",
                "POST": "chatbot.create",
                "PUT": "chatbot.update",
                "DELETE": "chatbot.delete",
            },
            "/api/v1/chatbots/{id}/deploy": {"POST": "chatbot.deploy"},
            # Analytics
            "/api/v1/analytics": {"GET": "analytics.read"},
            # Billing
            "/api/v1/billing": {
                "GET": "billing.read",
                "POST": "billing.manage",
                "PUT": "billing.manage",
            },
        }

        self.security = HTTPBearer(auto_error=False)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request through authorization middleware"""

        start_time = datetime.utcnow()

        try:
            # Skip authorization for excluded paths
            if self._should_skip_authorization(request.url.path):
                return await call_next(request)

            # Extract user from token
            user = await self._get_user_from_request(request)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Check permissions for this endpoint
            await self._check_endpoint_permission(request, user)

            # Add user to request state for downstream use
            request.state.current_user = user

            # Process request
            response = await call_next(request)

            # Log successful authorization
            await self._log_authorization_event(
                request=request,
                user=user,
                success=True,
                duration=(datetime.utcnow() - start_time).total_seconds(),
            )

            return response

        except HTTPException as e:
            # Log failed authorization
            await self._log_authorization_event(
                request=request,
                user=getattr(request.state, "current_user", None),
                success=False,
                error=str(e.detail),
                status_code=e.status_code,
                duration=(datetime.utcnow() - start_time).total_seconds(),
            )
            raise

        except Exception as e:
            logger.error(f"Authorization middleware error: {e}")
            await self._log_authorization_event(
                request=request,
                user=getattr(request.state, "current_user", None),
                success=False,
                error=str(e),
                status_code=500,
                duration=(datetime.utcnow() - start_time).total_seconds(),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization check failed",
            )

    def _should_skip_authorization(self, path: str) -> bool:
        """Check if path should skip authorization"""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)

    async def _get_user_from_request(self, request: Request) -> Optional[User]:
        """Extract and validate user from request token"""
        try:
            # Get authorization header
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None

            token = authorization.split(" ")[1]

            # Get database session
            async for db in get_db_session():
                try:
                    user = await get_current_user_from_token(token, db)
                    return user
                finally:
                    await db.close()
                    break

        except Exception as e:
            logger.error(f"Failed to get user from request: {e}")
            return None

    async def _check_endpoint_permission(self, request: Request, user: User) -> None:
        """Check if user has permission for this endpoint"""

        path = request.url.path
        method = request.method

        # Find permission required for this endpoint
        required_permission = self._get_required_permission(path, method)

        if not required_permission:
            # No specific permission required
            return

        # Extract resource information from path
        resource_type, resource_id = self._extract_resource_info(path)

        # Get database session for permission check
        async for db in get_db_session():
            try:
                has_permission = await authorization_service.check_permission(
                    user=user,
                    permission_name=required_permission,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    db=db,
                )

                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission '{required_permission}' required",
                    )

            finally:
                await db.close()
                break

    def _get_required_permission(self, path: str, method: str) -> Optional[str]:
        """Get required permission for path and method"""

        # Check exact path match first
        if path in self.permission_map:
            return self.permission_map[path].get(method)

        # Check pattern matches (for paths with IDs)
        for pattern, permissions in self.permission_map.items():
            if self._path_matches_pattern(path, pattern):
                return permissions.get(method)

        return None

    def _path_matches_pattern(self, path: str, pattern: str) -> bool:
        """Check if path matches pattern with placeholders"""
        path_parts = path.strip("/").split("/")
        pattern_parts = pattern.strip("/").split("/")

        if len(path_parts) != len(pattern_parts):
            return False

        for path_part, pattern_part in zip(path_parts, pattern_parts):
            if pattern_part.startswith("{") and pattern_part.endswith("}"):
                # This is a placeholder, matches any value
                continue
            elif path_part != pattern_part:
                return False

        return True

    def _extract_resource_info(self, path: str) -> tuple[Optional[str], Optional[int]]:
        """Extract resource type and ID from path"""

        path_parts = path.strip("/").split("/")

        # Map path prefixes to resource types
        resource_type_map = {
            "users": "user",
            "clients": "client",
            "chatbots": "chatbot",
            "analytics": "analytics",
            "billing": "billing",
        }

        resource_type = None
        resource_id = None

        for i, part in enumerate(path_parts):
            if part in resource_type_map:
                resource_type = resource_type_map[part]
                # Check if next part is an ID
                if i + 1 < len(path_parts):
                    try:
                        resource_id = int(path_parts[i + 1])
                    except ValueError:
                        pass
                break

        return resource_type, resource_id

    async def _log_authorization_event(
        self,
        request: Request,
        user: Optional[User],
        success: bool,
        error: Optional[str] = None,
        status_code: Optional[int] = None,
        duration: Optional[float] = None,
    ) -> None:
        """Log authorization event for audit purposes"""

        try:
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user.id if user else None,
                "user_email": user.email if user else None,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "ip_address": request.client.host if request.client else None,
                "user_agent": request.headers.get("User-Agent"),
                "success": success,
                "error": error,
                "status_code": status_code,
                "duration_seconds": duration,
            }

            if success:
                logger.info(f"Authorization success: {json.dumps(log_data)}")
            else:
                logger.warning(f"Authorization failure: {json.dumps(log_data)}")

        except Exception as e:
            logger.error(f"Failed to log authorization event: {e}")


# Decorator for manual permission checking
def require_permission_manual(
    permission_name: str, resource_type: Optional[str] = None
):
    """
    Decorator for manual permission checking in route handlers
    Use this when you need custom permission logic
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request and user from function arguments
            request = None
            user = None

            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    user = getattr(request.state, "current_user", None)
                    break

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Extract resource_id from kwargs if available
            resource_id = kwargs.get("resource_id") or kwargs.get("id")

            # Get database session
            async for db in get_db_session():
                try:
                    has_permission = await authorization_service.check_permission(
                        user=user,
                        permission_name=permission_name,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        db=db,
                    )

                    if not has_permission:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Permission '{permission_name}' required",
                        )

                finally:
                    await db.close()
                    break

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Context manager for temporary permission elevation
class PermissionContext:
    """Context manager for temporary permission elevation"""

    def __init__(
        self,
        user: User,
        permission: str,
        resource_type: str = None,
        resource_id: int = None,
    ):
        self.user = user
        self.permission = permission
        self.resource_type = resource_type
        self.resource_id = resource_id
        self._original_permissions = None

    async def __aenter__(self):
        # Store original permissions (simplified for demo)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Restore original permissions (simplified for demo)
        pass

    async def check_permission(self, db: AsyncSession) -> bool:
        """Check if permission is granted in this context"""
        return await authorization_service.check_permission(
            user=self.user,
            permission_name=self.permission,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            db=db,
        )
