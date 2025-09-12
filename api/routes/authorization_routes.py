"""
Authorization API Routes

This module provides comprehensive REST API endpoints for authorization management including:
- Role management (CRUD operations)
- Permission management and assignment
- User role assignments
- Permission checking and validation
- Audit trail access
- Organization and team permission management
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload, joinedload
from pydantic import BaseModel, Field, validator

from core.database import get_db_session
from core.auth import get_current_user, get_current_active_user
from models.database_schema import User
from models.authorization_models import (
    Role, Permission, UserPermission, Organization, Team,
    OrganizationMembership, TeamMembership, PermissionAudit,
    PermissionType, ResourceType, PermissionScope,
    user_roles, role_permissions
)
from services.authorization_service import authorization_service, require_permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["authorization"])
security = HTTPBearer()

# Pydantic Models for Request/Response

class PermissionBase(BaseModel):
    name: str = Field(..., description="Permission name")
    display_name: str = Field(..., description="Human readable permission name")
    description: Optional[str] = Field(None, description="Permission description")
    permission_type: str = Field(..., description="Permission type (read, write, delete, etc.)")
    resource_type: str = Field(..., description="Resource type this permission applies to")
    scope: str = Field(..., description="Permission scope (global, organization, team, resource)")

class PermissionCreate(PermissionBase):
    is_system_permission: bool = Field(False, description="Whether this is a system permission")

class PermissionUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class PermissionResponse(PermissionBase):
    id: int
    is_system_permission: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str = Field(..., description="Role name")
    display_name: str = Field(..., description="Human readable role name")
    description: Optional[str] = Field(None, description="Role description")
    scope: str = Field(..., description="Role scope")
    color: Optional[str] = Field(None, description="Role color for UI")
    icon: Optional[str] = Field(None, description="Role icon")

class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default_factory=list, description="List of permission IDs")
    max_assignees: Optional[int] = Field(None, description="Maximum number of users that can have this role")
    is_assignable: bool = Field(True, description="Whether this role can be assigned to users")

class RoleUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    max_assignees: Optional[int] = None
    is_assignable: Optional[bool] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[int]] = None

class RoleResponse(RoleBase):
    id: int
    is_system_role: bool
    is_assignable: bool
    is_active: bool
    max_assignees: Optional[int]
    created_at: datetime
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True

class UserRoleAssignment(BaseModel):
    user_id: int = Field(..., description="User ID")
    role_id: int = Field(..., description="Role ID")
    expires_at: Optional[datetime] = Field(None, description="Role expiration date")

class UserPermissionGrant(BaseModel):
    user_id: int = Field(..., description="User ID")
    permission_id: int = Field(..., description="Permission ID")
    resource_type: Optional[str] = Field(None, description="Resource type")
    resource_id: Optional[int] = Field(None, description="Resource ID")
    expires_at: Optional[datetime] = Field(None, description="Permission expiration date")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Additional conditions")

class PermissionCheckRequest(BaseModel):
    permission_name: str = Field(..., description="Permission name to check")
    resource_type: Optional[str] = Field(None, description="Resource type")
    resource_id: Optional[int] = Field(None, description="Resource ID")

class PermissionCheckResponse(BaseModel):
    has_permission: bool = Field(..., description="Whether user has the permission")
    reason: Optional[str] = Field(None, description="Reason for the result")

class UserPermissionsResponse(BaseModel):
    user_id: int
    roles: List[Dict[str, Any]]
    direct_permissions: List[Dict[str, Any]]
    effective_permissions: List[str]
    is_super_admin: bool

class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    permission_id: Optional[int]
    role_id: Optional[int]
    resource_type: Optional[str]
    resource_id: Optional[int]
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    reason: Optional[str]
    performed_by: int
    performed_at: datetime
    
    class Config:
        from_attributes = True


# Permission Management Endpoints

@router.get("/permissions", response_model=List[PermissionResponse])
@require_permission("system.read")
async def list_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get list of all permissions with optional filtering"""
    try:
        query = select(Permission).where(Permission.is_active == True)
        
        # Apply filters
        if scope:
            query = query.where(Permission.scope == scope)
        if resource_type:
            query = query.where(Permission.resource_type == resource_type)
        if search:
            query = query.where(
                or_(
                    Permission.name.ilike(f"%{search}%"),
                    Permission.display_name.ilike(f"%{search}%"),
                    Permission.description.ilike(f"%{search}%")
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Permission.name)
        
        result = await db.execute(query)
        permissions = result.scalars().all()
        
        return [PermissionResponse.from_orm(perm) for perm in permissions]
        
    except Exception as e:
        logger.error(f"Failed to list permissions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve permissions"
        )

@router.post("/permissions", response_model=PermissionResponse)
@require_permission("system.manage")
async def create_permission(
    permission_data: PermissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new permission"""
    try:
        # Check if permission already exists
        existing = await db.execute(
            select(Permission).where(Permission.name == permission_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Permission with this name already exists"
            )
        
        permission = Permission(
            name=permission_data.name,
            display_name=permission_data.display_name,
            description=permission_data.description,
            permission_type=permission_data.permission_type,
            resource_type=permission_data.resource_type,
            scope=permission_data.scope,
            is_system_permission=permission_data.is_system_permission
        )
        
        db.add(permission)
        await db.commit()
        await db.refresh(permission)
        
        logger.info(f"Permission '{permission.name}' created by user {current_user.id}")
        return PermissionResponse.from_orm(permission)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create permission: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create permission"
        )

@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
@require_permission("system.read")
async def get_permission(
    permission_id: int = Path(..., description="Permission ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get permission by ID"""
    try:
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        return PermissionResponse.from_orm(permission)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get permission {permission_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve permission"
        )

@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
@require_permission("system.manage")
async def update_permission(
    permission_id: int = Path(..., description="Permission ID"),
    update_data: PermissionUpdate = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update permission"""
    try:
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        # Check if it's a system permission and restrict updates
        if permission.is_system_permission and update_data.display_name is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify system permissions"
            )
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(permission, field, value)
        
        await db.commit()
        await db.refresh(permission)
        
        logger.info(f"Permission {permission_id} updated by user {current_user.id}")
        return PermissionResponse.from_orm(permission)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update permission {permission_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permission"
        )

@router.delete("/permissions/{permission_id}")
@require_permission("system.manage")
async def delete_permission(
    permission_id: int = Path(..., description="Permission ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete permission (soft delete)"""
    try:
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Permission not found"
            )
        
        if permission.is_system_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete system permissions"
            )
        
        # Soft delete
        permission.is_active = False
        await db.commit()
        
        logger.info(f"Permission {permission_id} deleted by user {current_user.id}")
        return {"message": "Permission deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete permission {permission_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete permission"
        )


# Role Management Endpoints

@router.get("/roles", response_model=List[RoleResponse])
@require_permission("system.read")
async def list_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    scope: Optional[str] = Query(None),
    include_permissions: bool = Query(False),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get list of all roles with optional filtering"""
    try:
        query = select(Role).where(Role.is_active == True)
        
        if include_permissions:
            query = query.options(selectinload(Role.permissions))
        
        # Apply filters
        if scope:
            query = query.where(Role.scope == scope)
        if search:
            query = query.where(
                or_(
                    Role.name.ilike(f"%{search}%"),
                    Role.display_name.ilike(f"%{search}%"),
                    Role.description.ilike(f"%{search}%")
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Role.name)
        
        result = await db.execute(query)
        roles = result.scalars().all()
        
        return [RoleResponse.from_orm(role) for role in roles]
        
    except Exception as e:
        logger.error(f"Failed to list roles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve roles"
        )

@router.post("/roles", response_model=RoleResponse)
@require_permission("system.manage")
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new role"""
    try:
        # Check if role already exists
        existing = await db.execute(
            select(Role).where(Role.name == role_data.name)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role with this name already exists"
            )
        
        # Create role
        role = Role(
            name=role_data.name,
            display_name=role_data.display_name,
            description=role_data.description,
            scope=role_data.scope,
            color=role_data.color,
            icon=role_data.icon,
            max_assignees=role_data.max_assignees,
            is_assignable=role_data.is_assignable
        )
        
        db.add(role)
        await db.flush()  # Get the role ID
        
        # Assign permissions
        if role_data.permission_ids:
            # Verify permissions exist
            perm_result = await db.execute(
                select(Permission).where(Permission.id.in_(role_data.permission_ids))
            )
            permissions = perm_result.scalars().all()
            
            if len(permissions) != len(role_data.permission_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="One or more permissions not found"
                )
            
            # Add permissions to role
            for permission in permissions:
                role.permissions.append(permission)
        
        await db.commit()
        await db.refresh(role)
        
        # Load permissions for response
        await db.execute(
            select(Role).options(selectinload(Role.permissions)).where(Role.id == role.id)
        )
        
        logger.info(f"Role '{role.name}' created by user {current_user.id}")
        return RoleResponse.from_orm(role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create role: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create role"
        )

@router.get("/roles/{role_id}", response_model=RoleResponse)
@require_permission("system.read")
async def get_role(
    role_id: int = Path(..., description="Role ID"),
    include_permissions: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get role by ID"""
    try:
        query = select(Role).where(Role.id == role_id)
        
        if include_permissions:
            query = query.options(selectinload(Role.permissions))
        
        result = await db.execute(query)
        role = result.scalar_one_or_none()
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        
        return RoleResponse.from_orm(role)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get role {role_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve role"
        )


# User Permission Management

@router.post("/users/{user_id}/roles")
@require_permission("user.manage")
async def assign_user_role(
    user_id: int = Path(..., description="User ID"),
    assignment: UserRoleAssignment = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Assign role to user"""
    try:
        # Verify user exists
        user_result = await db.execute(select(User).where(User.id == user_id))
        if not user_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        success = await authorization_service.assign_role(
            user_id=user_id,
            role_id=assignment.role_id,
            assigned_by=current_user.id,
            expires_at=assignment.expires_at,
            db=db
        )
        
        if success:
            return {"message": "Role assigned successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to assign role"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to assign role to user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign role"
        )

@router.delete("/users/{user_id}/roles/{role_id}")
@require_permission("user.manage")
async def revoke_user_role(
    user_id: int = Path(..., description="User ID"),
    role_id: int = Path(..., description="Role ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Revoke role from user"""
    try:
        success = await authorization_service.revoke_role(
            user_id=user_id,
            role_id=role_id,
            revoked_by=current_user.id,
            db=db
        )
        
        if success:
            return {"message": "Role revoked successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role assignment not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to revoke role from user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke role"
        )

@router.post("/users/{user_id}/permissions")
@require_permission("user.manage")
async def grant_user_permission(
    user_id: int = Path(..., description="User ID"),
    grant: UserPermissionGrant = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Grant direct permission to user"""
    try:
        success = await authorization_service.grant_permission(
            user_id=user_id,
            permission_id=grant.permission_id,
            granted_by=current_user.id,
            resource_type=grant.resource_type,
            resource_id=grant.resource_id,
            expires_at=grant.expires_at,
            conditions=grant.conditions,
            db=db
        )
        
        if success:
            return {"message": "Permission granted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to grant permission"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to grant permission to user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to grant permission"
        )

@router.get("/users/{user_id}/permissions", response_model=UserPermissionsResponse)
@require_permission("user.read")
async def get_user_permissions(
    user_id: int = Path(..., description="User ID"),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all permissions for a user"""
    try:
        permissions = await authorization_service.get_user_permissions(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            db=db
        )
        
        return UserPermissionsResponse(
            user_id=user_id,
            **permissions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user permissions for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user permissions"
        )

@router.post("/users/{user_id}/check-permission", response_model=PermissionCheckResponse)
async def check_user_permission(
    user_id: int = Path(..., description="User ID"),
    check_request: PermissionCheckRequest = Body(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if user has specific permission"""
    try:
        # Get user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if current user can check this user's permissions
        if user_id != current_user.id:
            has_check_permission = await authorization_service.check_permission(
                user=current_user,
                permission_name="user.read",
                db=db
            )
            if not has_check_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot check other user's permissions"
                )
        
        has_permission = await authorization_service.check_permission(
            user=user,
            permission_name=check_request.permission_name,
            resource_type=check_request.resource_type,
            resource_id=check_request.resource_id,
            db=db
        )
        
        return PermissionCheckResponse(
            has_permission=has_permission,
            reason="Permission granted" if has_permission else "Permission denied"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check permission for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check permission"
        )


# Audit Trail

@router.get("/audit", response_model=List[AuditLogResponse])
@require_permission("system.read")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get audit logs with filtering"""
    try:
        query = select(PermissionAudit)
        
        # Apply filters
        if user_id:
            query = query.where(PermissionAudit.user_id == user_id)
        if action:
            query = query.where(PermissionAudit.action == action)
        if start_date:
            query = query.where(PermissionAudit.performed_at >= start_date)
        if end_date:
            query = query.where(PermissionAudit.performed_at <= end_date)
        
        # Apply pagination and ordering
        query = query.order_by(desc(PermissionAudit.performed_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        audit_logs = result.scalars().all()
        
        return [AuditLogResponse.from_orm(log) for log in audit_logs]
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )


# System Initialization

@router.post("/initialize-system")
@require_permission("system.admin")
async def initialize_authorization_system(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Initialize authorization system with default roles and permissions"""
    try:
        await authorization_service.initialize_system_data(db)
        
        logger.info(f"Authorization system initialized by user {current_user.id}")
        return {"message": "Authorization system initialized successfully"}
        
    except Exception as e:
        logger.error(f"Failed to initialize authorization system: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize authorization system"
        )
