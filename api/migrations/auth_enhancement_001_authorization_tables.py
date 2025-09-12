"""
Authorization System Database Migration

This migration creates all the necessary tables for the comprehensive
authorization system:
- Roles and permissions tables
- User-role and role-permission relationships
- Organizations and teams for multi-tenancy
- Permission auditing
- Direct user permissions with conditions
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'auth_enhancement_001'
down_revision = None  # First migration for authorization
branch_labels = None
depends_on = None


def upgrade():
    """Create authorization system tables"""
    
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scope', sa.String(20), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('is_system_role', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_assignable', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('max_assignees', sa.Integer(), nullable=True),
        sa.Column('parent_role_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_role_id'], ['roles.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('name')
    )
    
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('permission_type', sa.String(20), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('scope', sa.String(20), nullable=False),
        sa.Column('is_system_permission', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create role_permissions association table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    
    # Create user_roles association table with expiration support
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    
    # Create organizations table for multi-tenancy
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('plan_type', sa.String(20), nullable=True),
        sa.Column('subscription_expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('display_name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('parent_team_id', sa.Integer(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_team_id'], ['teams.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('organization_id', 'name')
    )
    
    # Create organization_memberships table
    op.create_table(
        'organization_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, default='member'),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('user_id', 'organization_id')
    )
    
    # Create team_memberships table
    op.create_table(
        'team_memberships',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, default='member'),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('invited_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['invited_by'], ['users.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('user_id', 'team_id')
    )
    
    # Create user_permissions table for direct permission grants
    op.create_table(
        'user_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('is_granted', sa.Boolean(), nullable=False, default=True),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('granted_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('granted_by', sa.Integer(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_by', sa.Integer(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['granted_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['revoked_by'], ['users.id'], ondelete='SET NULL')
    )
    
    # Create permission_audits table for tracking permission changes
    op.create_table(
        'permission_audits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('performed_by', sa.Integer(), nullable=False),
        sa.Column('performed_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('session_id', sa.String(100), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ondelete='RESTRICT')
    )
    
    # Create indexes for better performance
    op.create_index('idx_roles_name', 'roles', ['name'])
    op.create_index('idx_roles_scope', 'roles', ['scope'])
    op.create_index('idx_permissions_name', 'permissions', ['name'])
    op.create_index('idx_permissions_type_resource', 'permissions', ['permission_type', 'resource_type'])
    op.create_index('idx_user_roles_user_id', 'user_roles', ['user_id'])
    op.create_index('idx_user_roles_role_id', 'user_roles', ['role_id'])
    op.create_index('idx_user_roles_expires_at', 'user_roles', ['expires_at'])
    op.create_index('idx_role_permissions_role_id', 'role_permissions', ['role_id'])
    op.create_index('idx_role_permissions_permission_id', 'role_permissions', ['permission_id'])
    op.create_index('idx_organizations_name', 'organizations', ['name'])
    op.create_index('idx_teams_organization_id', 'teams', ['organization_id'])
    op.create_index('idx_teams_name', 'teams', ['name'])
    op.create_index('idx_organization_memberships_user_id', 'organization_memberships', ['user_id'])
    op.create_index('idx_organization_memberships_org_id', 'organization_memberships', ['organization_id'])
    op.create_index('idx_team_memberships_user_id', 'team_memberships', ['user_id'])
    op.create_index('idx_team_memberships_team_id', 'team_memberships', ['team_id'])
    op.create_index('idx_user_permissions_user_id', 'user_permissions', ['user_id'])
    op.create_index('idx_user_permissions_permission_id', 'user_permissions', ['permission_id'])
    op.create_index('idx_user_permissions_resource', 'user_permissions', ['resource_type', 'resource_id'])
    op.create_index('idx_user_permissions_granted', 'user_permissions', ['is_granted'])
    op.create_index('idx_user_permissions_expires_at', 'user_permissions', ['expires_at'])
    op.create_index('idx_permission_audits_user_id', 'permission_audits', ['user_id'])
    op.create_index('idx_permission_audits_action', 'permission_audits', ['action'])
    op.create_index('idx_permission_audits_performed_at', 'permission_audits', ['performed_at'])
    op.create_index('idx_permission_audits_performed_by', 'permission_audits', ['performed_by'])
    
    # Add authorization-related columns to users table if they don't exist
    try:
        op.add_column('users', sa.Column('is_super_admin', sa.Boolean(), nullable=False, default=False))
        op.add_column('users', sa.Column('default_organization_id', sa.Integer(), nullable=True))
        op.add_column('users', sa.Column('preferences', sa.JSON(), nullable=True))
        op.create_foreign_key('fk_users_default_organization', 'users', 'organizations', ['default_organization_id'], ['id'], ondelete='SET NULL')
    except Exception:
        # Columns might already exist
        pass


def downgrade():
    """Drop authorization system tables"""
    
    # Drop indexes first
    op.drop_index('idx_permission_audits_performed_by', 'permission_audits')
    op.drop_index('idx_permission_audits_performed_at', 'permission_audits')
    op.drop_index('idx_permission_audits_action', 'permission_audits')
    op.drop_index('idx_permission_audits_user_id', 'permission_audits')
    op.drop_index('idx_user_permissions_expires_at', 'user_permissions')
    op.drop_index('idx_user_permissions_granted', 'user_permissions')
    op.drop_index('idx_user_permissions_resource', 'user_permissions')
    op.drop_index('idx_user_permissions_permission_id', 'user_permissions')
    op.drop_index('idx_user_permissions_user_id', 'user_permissions')
    op.drop_index('idx_team_memberships_team_id', 'team_memberships')
    op.drop_index('idx_team_memberships_user_id', 'team_memberships')
    op.drop_index('idx_organization_memberships_org_id', 'organization_memberships')
    op.drop_index('idx_organization_memberships_user_id', 'organization_memberships')
    op.drop_index('idx_teams_name', 'teams')
    op.drop_index('idx_teams_organization_id', 'teams')
    op.drop_index('idx_organizations_name', 'organizations')
    op.drop_index('idx_role_permissions_permission_id', 'role_permissions')
    op.drop_index('idx_role_permissions_role_id', 'role_permissions')
    op.drop_index('idx_user_roles_expires_at', 'user_roles')
    op.drop_index('idx_user_roles_role_id', 'user_roles')
    op.drop_index('idx_user_roles_user_id', 'user_roles')
    op.drop_index('idx_permissions_type_resource', 'permissions')
    op.drop_index('idx_permissions_name', 'permissions')
    op.drop_index('idx_roles_scope', 'roles')
    op.drop_index('idx_roles_name', 'roles')
    
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_table('permission_audits')
    op.drop_table('user_permissions')
    op.drop_table('team_memberships')
    op.drop_table('organization_memberships')
    op.drop_table('teams')
    op.drop_table('organizations')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
    
    # Remove authorization columns from users table
    try:
        op.drop_constraint('fk_users_default_organization', 'users', type_='foreignkey')
        op.drop_column('users', 'preferences')
        op.drop_column('users', 'default_organization_id')
        op.drop_column('users', 'is_super_admin')
    except Exception:
        # Columns might not exist
        pass
