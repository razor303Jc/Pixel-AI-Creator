"""
Authorization Enhancement Models

This module provides enhanced authorization features including:
- Fine-grained permission system
- Dynamic role assignment
- Resource-based access control
- Permission inheritance and delegation
- Hierarchical role management
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
    UniqueConstraint,
    CheckConstraint,
    Table,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime
from enum import Enum

from models.database_schema import Base, User


class PermissionType(str, Enum):
    """Permission types for fine-grained access control"""

    # Object-level permissions
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"

    # Advanced permissions
    ADMIN = "admin"
    MANAGE = "manage"
    EXECUTE = "execute"
    APPROVE = "approve"

    # Special permissions
    OWNER = "owner"
    DELEGATE = "delegate"
    INHERIT = "inherit"


class ResourceType(str, Enum):
    """Resource types for access control"""

    # Core resources
    USER = "user"
    CLIENT = "client"
    CHATBOT = "chatbot"
    CONVERSATION = "conversation"
    MESSAGE = "message"

    # System resources
    ANALYTICS = "analytics"
    REPORTS = "reports"
    SYSTEM = "system"
    API = "api"

    # Business resources
    BILLING = "billing"
    ORGANIZATION = "organization"
    TEAM = "team"
    PROJECT = "project"


class PermissionScope(str, Enum):
    """Permission scope levels"""

    GLOBAL = "global"  # System-wide permissions
    ORGANIZATION = "organization"  # Organization-level
    TEAM = "team"  # Team-level
    PROJECT = "project"  # Project-level
    RESOURCE = "resource"  # Individual resource
    SELF = "self"  # Own resources only


# === AUTHORIZATION TABLES ===

# Many-to-many association tables
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("assigned_at", DateTime, server_default=func.now()),
    Column("assigned_by", Integer, ForeignKey("users.id")),
    Column("expires_at", DateTime, nullable=True),
    Index("idx_user_roles_user_id", "user_id"),
    Index("idx_user_roles_role_id", "role_id"),
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("granted_at", DateTime, server_default=func.now()),
    Column("granted_by", Integer, ForeignKey("users.id")),
    Index("idx_role_permissions_role_id", "role_id"),
    Index("idx_role_permissions_permission_id", "permission_id"),
)


class Role(Base):
    """Role model for role-based access control"""

    __tablename__ = "roles"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Role information
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Role hierarchy
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)
    hierarchy_level = Column(Integer, default=0, nullable=False)

    # Role properties
    is_system_role = Column(Boolean, default=False, nullable=False)
    is_assignable = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Scope and constraints
    scope = Column(
        String(50), default=PermissionScope.ORGANIZATION.value, nullable=False
    )
    max_assignees = Column(
        Integer, nullable=True
    )  # Limit number of users with this role

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    parent_role = relationship("Role", remote_side=[id], back_populates="child_roles")
    child_roles = relationship("Role", back_populates="parent_role")
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship(
        "Permission", secondary=role_permissions, back_populates="roles"
    )
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        Index("idx_roles_name", "name"),
        Index("idx_roles_parent", "parent_role_id"),
        Index("idx_roles_scope", "scope"),
        Index("idx_roles_active", "is_active"),
        CheckConstraint("hierarchy_level >= 0", name="ck_role_hierarchy_level"),
        CheckConstraint(
            "max_assignees IS NULL OR max_assignees > 0", name="ck_role_max_assignees"
        ),
    )


class Permission(Base):
    """Permission model for fine-grained access control"""

    __tablename__ = "permissions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Permission identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Permission properties
    permission_type = Column(String(50), nullable=False)  # PermissionType enum
    resource_type = Column(String(50), nullable=False)  # ResourceType enum
    scope = Column(String(50), default=PermissionScope.RESOURCE.value, nullable=False)

    # Permission attributes
    is_system_permission = Column(Boolean, default=False, nullable=False)
    is_delegatable = Column(Boolean, default=False, nullable=False)
    requires_approval = Column(Boolean, default=False, nullable=False)

    # Permission constraints
    conditions = Column(JSON, nullable=True)  # Additional conditions for permission

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    roles = relationship(
        "Role", secondary=role_permissions, back_populates="permissions"
    )
    direct_grants = relationship("UserPermission", back_populates="permission")
    creator = relationship("User", foreign_keys=[created_by])

    # Indexes
    __table_args__ = (
        Index("idx_permissions_name", "name"),
        Index("idx_permissions_type", "permission_type"),
        Index("idx_permissions_resource", "resource_type"),
        Index("idx_permissions_scope", "scope"),
        UniqueConstraint(
            "permission_type",
            "resource_type",
            "scope",
            name="uq_permission_type_resource_scope",
        ),
    )


class UserPermission(Base):
    """Direct user permission grants (bypassing roles)"""

    __tablename__ = "user_permissions"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Grant information
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    permission_id = Column(
        Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )

    # Resource-specific grants
    resource_type = Column(String(50), nullable=True)  # ResourceType enum
    resource_id = Column(Integer, nullable=True)  # Specific resource ID

    # Grant properties
    is_granted = Column(
        Boolean, default=True, nullable=False
    )  # Can be False for explicit deny
    is_inherited = Column(Boolean, default=False, nullable=False)
    is_delegated = Column(Boolean, default=False, nullable=False)

    # Grant constraints
    conditions = Column(JSON, nullable=True)  # Additional conditions
    expires_at = Column(DateTime, nullable=True)

    # Metadata
    granted_at = Column(DateTime, server_default=func.now(), nullable=False)
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship(
        "User", foreign_keys=[user_id], back_populates="direct_permissions"
    )
    permission = relationship("Permission", back_populates="direct_grants")
    granter = relationship("User", foreign_keys=[granted_by])
    revoker = relationship("User", foreign_keys=[revoked_by])

    # Indexes
    __table_args__ = (
        Index("idx_user_permissions_user_id", "user_id"),
        Index("idx_user_permissions_permission_id", "permission_id"),
        Index("idx_user_permissions_resource", "resource_type", "resource_id"),
        Index("idx_user_permissions_granted", "is_granted"),
        Index("idx_user_permissions_expires", "expires_at"),
        UniqueConstraint(
            "user_id",
            "permission_id",
            "resource_type",
            "resource_id",
            name="uq_user_permission_resource",
        ),
    )


class Organization(Base):
    """Organization model for multi-tenancy"""

    __tablename__ = "organizations"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Organization information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Organization settings
    is_active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(String(50), default="free", nullable=False)
    settings = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    memberships = relationship("OrganizationMembership", back_populates="organization")
    teams = relationship("Team", back_populates="organization")

    # Indexes
    __table_args__ = (
        Index("idx_organizations_name", "name"),
        Index("idx_organizations_active", "is_active"),
        Index("idx_organizations_tier", "subscription_tier"),
    )


class OrganizationMembership(Base):
    """Organization membership for users"""

    __tablename__ = "organization_memberships"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Membership information
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # Membership properties
    is_active = Column(Boolean, default=True, nullable=False)
    is_owner = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    # Metadata
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    left_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    organization = relationship("Organization", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by])

    # Indexes
    __table_args__ = (
        Index("idx_org_memberships_user_id", "user_id"),
        Index("idx_org_memberships_org_id", "organization_id"),
        Index("idx_org_memberships_active", "is_active"),
        UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )


class Team(Base):
    """Team model for project organization"""

    __tablename__ = "teams"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Team information
    name = Column(String(200), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Team properties
    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    settings = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="teams")
    creator = relationship("User", foreign_keys=[created_by])
    memberships = relationship("TeamMembership", back_populates="team")

    # Indexes
    __table_args__ = (
        Index("idx_teams_name", "name"),
        Index("idx_teams_org_id", "organization_id"),
        Index("idx_teams_active", "is_active"),
    )


class TeamMembership(Base):
    """Team membership for users"""

    __tablename__ = "team_memberships"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Membership information
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    team_id = Column(
        Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False
    )

    # Membership properties
    is_active = Column(Boolean, default=True, nullable=False)
    is_lead = Column(Boolean, default=False, nullable=False)
    role_in_team = Column(String(100), nullable=True)

    # Metadata
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    left_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    team = relationship("Team", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by])

    # Indexes
    __table_args__ = (
        Index("idx_team_memberships_user_id", "user_id"),
        Index("idx_team_memberships_team_id", "team_id"),
        Index("idx_team_memberships_active", "is_active"),
        UniqueConstraint("user_id", "team_id", name="uq_user_team"),
    )


class PermissionAudit(Base):
    """Audit trail for permission changes"""

    __tablename__ = "permission_audits"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Audit information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # grant, revoke, modify
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=True)

    # Resource context
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(Integer, nullable=True)

    # Audit details
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)

    # Metadata
    performed_at = Column(DateTime, server_default=func.now(), nullable=False)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    performer = relationship("User", foreign_keys=[performed_by])
    permission = relationship("Permission")
    role = relationship("Role")

    # Indexes
    __table_args__ = (
        Index("idx_permission_audits_user_id", "user_id"),
        Index("idx_permission_audits_performed_at", "performed_at"),
        Index("idx_permission_audits_action", "action"),
        Index("idx_permission_audits_performer", "performed_by"),
    )


# Update User model to include authorization relationships
def update_user_model():
    """Update the User model with authorization relationships"""

    # Add relationships to User model
    User.roles = relationship("Role", secondary=user_roles, back_populates="users")
    User.direct_permissions = relationship(
        "UserPermission", foreign_keys=[UserPermission.user_id], back_populates="user"
    )
    User.organization_memberships = relationship(
        "OrganizationMembership", foreign_keys=[OrganizationMembership.user_id]
    )
    User.team_memberships = relationship(
        "TeamMembership", foreign_keys=[TeamMembership.user_id]
    )


# === PYDANTIC MODELS ===


class RoleCreate(BaseModel):
    """Pydantic model for role creation"""

    name: str = Field(..., min_length=2, max_length=100)
    display_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    parent_role_id: Optional[int] = None
    scope: PermissionScope = PermissionScope.ORGANIZATION
    is_assignable: bool = True
    max_assignees: Optional[int] = None


class RoleUpdate(BaseModel):
    """Pydantic model for role updates"""

    display_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    is_assignable: Optional[bool] = None
    max_assignees: Optional[int] = None


class RoleResponse(BaseModel):
    """Pydantic model for role responses"""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    parent_role_id: Optional[int]
    hierarchy_level: int
    scope: str
    is_system_role: bool
    is_assignable: bool
    is_active: bool
    max_assignees: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionCreate(BaseModel):
    """Pydantic model for permission creation"""

    name: str = Field(..., min_length=2, max_length=100)
    display_name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    permission_type: PermissionType
    resource_type: ResourceType
    scope: PermissionScope = PermissionScope.RESOURCE
    is_delegatable: bool = False
    requires_approval: bool = False
    conditions: Optional[Dict[str, Any]] = None


class PermissionResponse(BaseModel):
    """Pydantic model for permission responses"""

    id: int
    name: str
    display_name: str
    description: Optional[str]
    permission_type: str
    resource_type: str
    scope: str
    is_system_permission: bool
    is_delegatable: bool
    requires_approval: bool
    conditions: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class UserPermissionGrant(BaseModel):
    """Pydantic model for granting permissions to users"""

    user_id: int
    permission_id: int
    resource_type: Optional[ResourceType] = None
    resource_id: Optional[int] = None
    is_granted: bool = True
    conditions: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class RoleAssignment(BaseModel):
    """Pydantic model for role assignments"""

    user_id: int
    role_id: int
    expires_at: Optional[datetime] = None


class UserPermissionsResponse(BaseModel):
    """Pydantic model for user permissions response"""

    user_id: int
    roles: List[RoleResponse]
    direct_permissions: List[PermissionResponse]
    effective_permissions: List[str]  # Flattened list of all permissions

    class Config:
        from_attributes = True


class OrganizationCreate(BaseModel):
    """Pydantic model for organization creation"""

    name: str = Field(..., min_length=2, max_length=200)
    display_name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    subscription_tier: str = "free"
    settings: Optional[Dict[str, Any]] = None


class TeamCreate(BaseModel):
    """Pydantic model for team creation"""

    name: str = Field(..., min_length=2, max_length=200)
    display_name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    organization_id: int
    settings: Optional[Dict[str, Any]] = None
