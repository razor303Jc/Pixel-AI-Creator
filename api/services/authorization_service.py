"""
Authorization Service

This service provides comprehensive authorization functionality including:
- Permission checking and validation
- Role-based access control (RBAC)
- Resource-based access control
- Dynamic role assignment
- Permission inheritance and delegation
- Multi-tenant organization support
"""

import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status
from functools import wraps
import asyncio

from models.authorization_models import (
    Role, Permission, UserPermission, Organization, Team,
    OrganizationMembership, TeamMembership, PermissionAudit,
    PermissionType, ResourceType, PermissionScope,
    update_user_model
)
from models.database_schema import User

logger = logging.getLogger(__name__)

# Call the function to update User model with authorization relationships
update_user_model()


class AuthorizationService:
    """Comprehensive authorization service"""
    
    def __init__(self):
        # Cache for frequently accessed permissions
        self._permission_cache = {}
        self._role_cache = {}
        self._cache_ttl = 300  # 5 minutes
        
        # Built-in system roles and permissions
        self.system_roles = {
            "super_admin": {
                "display_name": "Super Administrator",
                "description": "Full system access with all permissions",
                "scope": PermissionScope.GLOBAL,
                "permissions": ["*"]  # All permissions
            },
            "org_admin": {
                "display_name": "Organization Administrator", 
                "description": "Full access within organization",
                "scope": PermissionScope.ORGANIZATION,
                "permissions": ["manage_organization", "manage_users", "manage_teams"]
            },
            "team_lead": {
                "display_name": "Team Lead",
                "description": "Manage team members and projects",
                "scope": PermissionScope.TEAM,
                "permissions": ["manage_team", "manage_projects", "view_analytics"]
            },
            "user": {
                "display_name": "Standard User",
                "description": "Basic user permissions",
                "scope": PermissionScope.RESOURCE,
                "permissions": ["read_own", "update_own"]
            }
        }
        
        self.system_permissions = {
            # System permissions
            "system.admin": ("admin", "system", "global"),
            "system.manage": ("manage", "system", "global"),
            "system.read": ("read", "system", "global"),
            
            # User permissions
            "user.create": ("create", "user", "organization"),
            "user.read": ("read", "user", "organization"),
            "user.update": ("update", "user", "organization"),
            "user.delete": ("delete", "user", "organization"),
            "user.manage": ("manage", "user", "organization"),
            
            # Client permissions
            "client.create": ("create", "client", "organization"),
            "client.read": ("read", "client", "organization"),
            "client.update": ("update", "client", "organization"),
            "client.delete": ("delete", "client", "organization"),
            "client.manage": ("manage", "client", "organization"),
            
            # Chatbot permissions
            "chatbot.create": ("create", "chatbot", "project"),
            "chatbot.read": ("read", "chatbot", "project"),
            "chatbot.update": ("update", "chatbot", "project"),
            "chatbot.delete": ("delete", "chatbot", "project"),
            "chatbot.deploy": ("execute", "chatbot", "project"),
            
            # Analytics permissions
            "analytics.read": ("read", "analytics", "organization"),
            "analytics.manage": ("manage", "analytics", "organization"),
            
            # Billing permissions
            "billing.read": ("read", "billing", "organization"),
            "billing.manage": ("manage", "billing", "organization"),
        }
    
    async def initialize_system_data(self, db: AsyncSession) -> None:
        """Initialize system roles and permissions"""
        try:
            # Create system permissions
            for perm_name, (perm_type, resource_type, scope) in self.system_permissions.items():
                existing = await db.execute(
                    select(Permission).where(Permission.name == perm_name)
                )
                if not existing.scalar_one_or_none():
                    permission = Permission(
                        name=perm_name,
                        display_name=perm_name.replace(".", " ").replace("_", " ").title(),
                        description=f"{perm_type.title()} permission for {resource_type}",
                        permission_type=perm_type,
                        resource_type=resource_type,
                        scope=scope,
                        is_system_permission=True
                    )
                    db.add(permission)
            
            # Create system roles
            for role_name, role_config in self.system_roles.items():
                existing = await db.execute(
                    select(Role).where(Role.name == role_name)
                )
                if not existing.scalar_one_or_none():
                    role = Role(
                        name=role_name,
                        display_name=role_config["display_name"],
                        description=role_config["description"],
                        scope=role_config["scope"].value,
                        is_system_role=True,
                        is_assignable=True
                    )
                    db.add(role)
            
            await db.commit()
            logger.info("System roles and permissions initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize system data: {e}")
            await db.rollback()
            raise
    
    async def check_permission(
        self,
        user: User,
        permission_name: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> bool:
        """
        Check if user has a specific permission
        
        Args:
            user: User object
            permission_name: Permission name to check
            resource_type: Optional resource type for resource-specific permissions
            resource_id: Optional resource ID for instance-specific permissions
            db: Database session
            
        Returns:
            Boolean indicating if user has permission
        """
        try:
            # Super admin bypass
            if await self._is_super_admin(user, db):
                return True
            
            # Check direct user permissions
            if await self._check_direct_permission(user.id, permission_name, resource_type, resource_id, db):
                return True
            
            # Check role-based permissions
            if await self._check_role_permissions(user.id, permission_name, resource_type, resource_id, db):
                return True
            
            # Check inherited permissions
            if await self._check_inherited_permissions(user.id, permission_name, resource_type, resource_id, db):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check failed for user {user.id}, permission {permission_name}: {e}")
            return False
    
    async def get_user_permissions(
        self,
        user_id: int,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Get all permissions for a user"""
        try:
            # Get user with relationships
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.roles).selectinload(Role.permissions),
                    selectinload(User.direct_permissions).selectinload(UserPermission.permission)
                )
                .where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Collect all permissions
            permissions = {
                "roles": [],
                "direct_permissions": [],
                "effective_permissions": set(),
                "is_super_admin": await self._is_super_admin(user, db)
            }
            
            # Role-based permissions
            for role in user.roles:
                role_data = {
                    "id": role.id,
                    "name": role.name,
                    "display_name": role.display_name,
                    "scope": role.scope,
                    "permissions": []
                }
                
                for permission in role.permissions:
                    perm_data = {
                        "id": permission.id,
                        "name": permission.name,
                        "type": permission.permission_type,
                        "resource": permission.resource_type,
                        "scope": permission.scope
                    }
                    role_data["permissions"].append(perm_data)
                    permissions["effective_permissions"].add(permission.name)
                
                permissions["roles"].append(role_data)
            
            # Direct permissions
            for user_perm in user.direct_permissions:
                if user_perm.is_granted and (not user_perm.expires_at or user_perm.expires_at > datetime.utcnow()):
                    # Check resource match
                    if resource_type and user_perm.resource_type and user_perm.resource_type != resource_type:
                        continue
                    if resource_id and user_perm.resource_id and user_perm.resource_id != resource_id:
                        continue
                    
                    perm_data = {
                        "id": user_perm.permission.id,
                        "name": user_perm.permission.name,
                        "type": user_perm.permission.permission_type,
                        "resource": user_perm.permission.resource_type,
                        "scope": user_perm.permission.scope,
                        "resource_id": user_perm.resource_id,
                        "expires_at": user_perm.expires_at
                    }
                    permissions["direct_permissions"].append(perm_data)
                    permissions["effective_permissions"].add(user_perm.permission.name)
            
            # Convert set to list for JSON serialization
            permissions["effective_permissions"] = list(permissions["effective_permissions"])
            
            return permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user permissions"
            )
    
    async def assign_role(
        self,
        user_id: int,
        role_id: int,
        assigned_by: int,
        expires_at: Optional[datetime] = None,
        db: AsyncSession = None
    ) -> bool:
        """Assign role to user"""
        try:
            # Verify role exists and is assignable
            role_result = await db.execute(
                select(Role).where(and_(Role.id == role_id, Role.is_assignable == True))
            )
            role = role_result.scalar_one_or_none()
            
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not found or not assignable"
                )
            
            # Check if user already has this role
            existing = await db.execute(
                select(user_roles).where(
                    and_(
                        user_roles.c.user_id == user_id,
                        user_roles.c.role_id == role_id
                    )
                )
            )
            
            if existing.scalar_one_or_none():
                return True  # Already assigned
            
            # Check max assignees limit
            if role.max_assignees:
                current_count = await db.execute(
                    select(func.count(user_roles.c.user_id)).where(user_roles.c.role_id == role_id)
                )
                if current_count.scalar() >= role.max_assignees:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Role assignment limit reached"
                    )
            
            # Insert role assignment
            await db.execute(
                user_roles.insert().values(
                    user_id=user_id,
                    role_id=role_id,
                    assigned_by=assigned_by,
                    expires_at=expires_at
                )
            )
            
            # Create audit record
            await self._create_audit_record(
                user_id=user_id,
                action="grant_role",
                role_id=role_id,
                performed_by=assigned_by,
                new_value={"role_id": role_id, "expires_at": expires_at.isoformat() if expires_at else None},
                db=db
            )
            
            await db.commit()
            
            # Clear cache
            self._clear_user_cache(user_id)
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to assign role {role_id} to user {user_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to assign role"
            )
    
    async def revoke_role(
        self,
        user_id: int,
        role_id: int,
        revoked_by: int,
        db: AsyncSession = None
    ) -> bool:
        """Revoke role from user"""
        try:
            # Delete role assignment
            result = await db.execute(
                user_roles.delete().where(
                    and_(
                        user_roles.c.user_id == user_id,
                        user_roles.c.role_id == role_id
                    )
                )
            )
            
            if result.rowcount == 0:
                return False  # Role was not assigned
            
            # Create audit record
            await self._create_audit_record(
                user_id=user_id,
                action="revoke_role",
                role_id=role_id,
                performed_by=revoked_by,
                old_value={"role_id": role_id},
                db=db
            )
            
            await db.commit()
            
            # Clear cache
            self._clear_user_cache(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke role {role_id} from user {user_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke role"
            )
    
    async def grant_permission(
        self,
        user_id: int,
        permission_id: int,
        granted_by: int,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        conditions: Optional[Dict[str, Any]] = None,
        db: AsyncSession = None
    ) -> bool:
        """Grant direct permission to user"""
        try:
            # Check if permission exists
            perm_result = await db.execute(
                select(Permission).where(Permission.id == permission_id)
            )
            permission = perm_result.scalar_one_or_none()
            
            if not permission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Permission not found"
                )
            
            # Check for existing grant
            existing = await db.execute(
                select(UserPermission).where(
                    and_(
                        UserPermission.user_id == user_id,
                        UserPermission.permission_id == permission_id,
                        UserPermission.resource_type == resource_type,
                        UserPermission.resource_id == resource_id
                    )
                )
            )
            
            existing_grant = existing.scalar_one_or_none()
            
            if existing_grant:
                # Update existing grant
                existing_grant.is_granted = True
                existing_grant.expires_at = expires_at
                existing_grant.conditions = conditions
                existing_grant.granted_by = granted_by
                existing_grant.granted_at = datetime.utcnow()
                existing_grant.revoked_at = None
                existing_grant.revoked_by = None
            else:
                # Create new grant
                user_permission = UserPermission(
                    user_id=user_id,
                    permission_id=permission_id,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    is_granted=True,
                    expires_at=expires_at,
                    conditions=conditions,
                    granted_by=granted_by
                )
                db.add(user_permission)
            
            # Create audit record
            await self._create_audit_record(
                user_id=user_id,
                action="grant_permission",
                permission_id=permission_id,
                performed_by=granted_by,
                resource_type=resource_type,
                resource_id=resource_id,
                new_value={
                    "permission_id": permission_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id,
                    "expires_at": expires_at.isoformat() if expires_at else None,
                    "conditions": conditions
                },
                db=db
            )
            
            await db.commit()
            
            # Clear cache
            self._clear_user_cache(user_id)
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to grant permission {permission_id} to user {user_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to grant permission"
            )
    
    async def revoke_permission(
        self,
        user_id: int,
        permission_id: int,
        revoked_by: int,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        db: AsyncSession = None
    ) -> bool:
        """Revoke direct permission from user"""
        try:
            # Find the permission grant
            result = await db.execute(
                select(UserPermission).where(
                    and_(
                        UserPermission.user_id == user_id,
                        UserPermission.permission_id == permission_id,
                        UserPermission.resource_type == resource_type,
                        UserPermission.resource_id == resource_id,
                        UserPermission.is_granted == True
                    )
                )
            )
            
            user_permission = result.scalar_one_or_none()
            
            if not user_permission:
                return False  # Permission was not granted
            
            # Revoke permission
            user_permission.is_granted = False
            user_permission.revoked_at = datetime.utcnow()
            user_permission.revoked_by = revoked_by
            
            # Create audit record
            await self._create_audit_record(
                user_id=user_id,
                action="revoke_permission",
                permission_id=permission_id,
                performed_by=revoked_by,
                resource_type=resource_type,
                resource_id=resource_id,
                old_value={
                    "permission_id": permission_id,
                    "resource_type": resource_type,
                    "resource_id": resource_id
                },
                db=db
            )
            
            await db.commit()
            
            # Clear cache
            self._clear_user_cache(user_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke permission {permission_id} from user {user_id}: {e}")
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke permission"
            )
    
    # Helper methods
    
    async def _is_super_admin(self, user: User, db: AsyncSession) -> bool:
        """Check if user is super admin"""
        try:
            result = await db.execute(
                select(Role)
                .join(user_roles)
                .where(
                    and_(
                        user_roles.c.user_id == user.id,
                        Role.name == "super_admin"
                    )
                )
            )
            return result.scalar_one_or_none() is not None
        except Exception:
            return False
    
    async def _check_direct_permission(
        self,
        user_id: int,
        permission_name: str,
        resource_type: Optional[str],
        resource_id: Optional[int],
        db: AsyncSession
    ) -> bool:
        """Check direct user permissions"""
        try:
            query = select(UserPermission).join(Permission).where(
                and_(
                    UserPermission.user_id == user_id,
                    Permission.name == permission_name,
                    UserPermission.is_granted == True,
                    or_(
                        UserPermission.expires_at.is_(None),
                        UserPermission.expires_at > datetime.utcnow()
                    )
                )
            )
            
            # Add resource filters if specified
            if resource_type:
                query = query.where(
                    or_(
                        UserPermission.resource_type.is_(None),
                        UserPermission.resource_type == resource_type
                    )
                )
            
            if resource_id:
                query = query.where(
                    or_(
                        UserPermission.resource_id.is_(None),
                        UserPermission.resource_id == resource_id
                    )
                )
            
            result = await db.execute(query)
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Error checking direct permission: {e}")
            return False
    
    async def _check_role_permissions(
        self,
        user_id: int,
        permission_name: str,
        resource_type: Optional[str],
        resource_id: Optional[int],
        db: AsyncSession
    ) -> bool:
        """Check role-based permissions"""
        try:
            result = await db.execute(
                select(Permission)
                .join(role_permissions)
                .join(Role)
                .join(user_roles)
                .where(
                    and_(
                        user_roles.c.user_id == user_id,
                        Permission.name == permission_name,
                        Role.is_active == True,
                        or_(
                            user_roles.c.expires_at.is_(None),
                            user_roles.c.expires_at > datetime.utcnow()
                        )
                    )
                )
            )
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Error checking role permissions: {e}")
            return False
    
    async def _check_inherited_permissions(
        self,
        user_id: int,
        permission_name: str,
        resource_type: Optional[str],
        resource_id: Optional[int],
        db: AsyncSession
    ) -> bool:
        """Check inherited permissions (placeholder for future implementation)"""
        # TODO: Implement permission inheritance logic
        return False
    
    async def _create_audit_record(
        self,
        user_id: int,
        action: str,
        performed_by: int,
        permission_id: Optional[int] = None,
        role_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        db: AsyncSession = None
    ) -> None:
        """Create audit record for permission changes"""
        try:
            audit = PermissionAudit(
                user_id=user_id,
                action=action,
                permission_id=permission_id,
                role_id=role_id,
                resource_type=resource_type,
                resource_id=resource_id,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                performed_by=performed_by
            )
            db.add(audit)
            
        except Exception as e:
            logger.error(f"Failed to create audit record: {e}")
    
    def _clear_user_cache(self, user_id: int) -> None:
        """Clear cached data for user"""
        cache_keys = [k for k in self._permission_cache.keys() if k.startswith(f"user_{user_id}_")]
        for key in cache_keys:
            del self._permission_cache[key]


# Global authorization service instance
authorization_service = AuthorizationService()


# Decorator for permission checking
def require_permission(permission_name: str, resource_type: Optional[str] = None):
    """Decorator to require specific permission for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current user from kwargs (must be injected by dependency)
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Extract resource_id from path parameters if available
            resource_id = kwargs.get('resource_id') or kwargs.get('id')
            
            # Check permission
            has_permission = await authorization_service.check_permission(
                user=current_user,
                permission_name=permission_name,
                resource_type=resource_type,
                resource_id=resource_id,
                db=db
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission_name}' required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
