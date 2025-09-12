"""
Advanced Authentication Migration

This migration creates tables for advanced authentication features:
- UserMFA: Multi-factor authentication settings
- SocialLogin: Social provider login records
- PasswordHistory: Password change history
- LoginAttempt: Login attempt logging
- DeviceInfo: Trusted device tracking
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "003_advanced_auth"
down_revision = "002_base_auth"  # Adjust based on your last migration
branch_labels = None
depends_on = None


def upgrade():
    """Create advanced authentication tables"""

    # Create enum types
    op.execute(
        """
        CREATE TYPE mfamethod AS ENUM (
            'TOTP', 'SMS', 'EMAIL', 'BACKUP_CODES'
        );
    """
    )

    op.execute(
        """
        CREATE TYPE socialprovider AS ENUM (
            'GOOGLE', 'GITHUB', 'LINKEDIN', 'MICROSOFT', 'FACEBOOK'
        );
    """
    )

    # UserMFA table
    op.create_table(
        "user_mfa",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "method",
            postgresql.ENUM("TOTP", "SMS", "EMAIL", "BACKUP_CODES", name="mfamethod"),
            nullable=False,
        ),
        sa.Column("secret_key_encrypted", sa.Text, nullable=True),
        sa.Column("backup_codes_encrypted", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, default=False, nullable=False),
        sa.Column("setup_completed", sa.Boolean, default=False, nullable=False),
        sa.Column("last_used", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        # Constraints
        sa.UniqueConstraint("user_id", "method", name="uq_user_mfa_method"),
        sa.Index("idx_user_mfa_user_id", "user_id"),
        sa.Index("idx_user_mfa_active", "is_active"),
    )

    # SocialLogin table
    op.create_table(
        "social_login",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "provider",
            postgresql.ENUM(
                "GOOGLE",
                "GITHUB",
                "LINKEDIN",
                "MICROSOFT",
                "FACEBOOK",
                name="socialprovider",
            ),
            nullable=False,
        ),
        sa.Column("provider_user_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("access_token", sa.Text, nullable=True),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("token_expires_at", sa.DateTime, nullable=True),
        sa.Column("user_info", sa.JSON, nullable=True),
        sa.Column("linked_at", sa.DateTime, nullable=True),
        sa.Column("last_login_at", sa.DateTime, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        # Constraints
        sa.UniqueConstraint(
            "provider", "provider_user_id", name="uq_social_provider_user"
        ),
        sa.Index("idx_social_login_user_id", "user_id"),
        sa.Index("idx_social_login_provider", "provider"),
        sa.Index("idx_social_login_email", "email"),
    )

    # PasswordHistory table
    op.create_table(
        "password_history",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("changed_by_user", sa.Boolean, default=True, nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        # Constraints
        sa.Index("idx_password_history_user_id", "user_id"),
        sa.Index("idx_password_history_created_at", "created_at"),
    )

    # LoginAttempt table
    op.create_table(
        "login_attempt",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("success", sa.Boolean, nullable=False),
        sa.Column("failure_reason", sa.String(255), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("device_info", sa.JSON, nullable=True),
        sa.Column(
            "attempted_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        # Constraints
        sa.Index("idx_login_attempt_user_id", "user_id"),
        sa.Index("idx_login_attempt_email", "email"),
        sa.Index("idx_login_attempt_ip", "ip_address"),
        sa.Index("idx_login_attempt_attempted_at", "attempted_at"),
        sa.Index("idx_login_attempt_success", "success"),
    )

    # DeviceInfo table
    op.create_table(
        "device_info",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("device_name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(100), nullable=True),
        sa.Column("browser", sa.String(255), nullable=True),
        sa.Column("os", sa.String(255), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("device_fingerprint", sa.String(255), nullable=True),
        sa.Column("is_trusted", sa.Boolean, default=False, nullable=False),
        sa.Column(
            "last_used", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        # Constraints
        sa.Index("idx_device_info_user_id", "user_id"),
        sa.Index("idx_device_info_trusted", "is_trusted"),
        sa.Index("idx_device_info_last_used", "last_used"),
    )

    # Add new columns to existing users table for advanced auth
    op.add_column("users", sa.Column("password_changed_at", sa.DateTime, nullable=True))
    op.add_column(
        "users", sa.Column("mfa_enabled", sa.Boolean, default=False, nullable=False)
    )
    op.add_column(
        "users", sa.Column("account_locked", sa.Boolean, default=False, nullable=False)
    )
    op.add_column("users", sa.Column("locked_until", sa.DateTime, nullable=True))
    op.add_column(
        "users",
        sa.Column("failed_login_attempts", sa.Integer, default=0, nullable=False),
    )
    op.add_column("users", sa.Column("last_failed_login", sa.DateTime, nullable=True))
    op.add_column(
        "users",
        sa.Column("force_password_change", sa.Boolean, default=False, nullable=False),
    )

    # Add indexes for new user columns
    op.create_index("idx_users_mfa_enabled", "users", ["mfa_enabled"])
    op.create_index("idx_users_account_locked", "users", ["account_locked"])
    op.create_index("idx_users_password_changed_at", "users", ["password_changed_at"])


def downgrade():
    """Drop advanced authentication tables"""

    # Remove indexes from users table
    op.drop_index("idx_users_password_changed_at", "users")
    op.drop_index("idx_users_account_locked", "users")
    op.drop_index("idx_users_mfa_enabled", "users")

    # Remove columns from users table
    op.drop_column("users", "force_password_change")
    op.drop_column("users", "last_failed_login")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "account_locked")
    op.drop_column("users", "mfa_enabled")
    op.drop_column("users", "password_changed_at")

    # Drop tables
    op.drop_table("device_info")
    op.drop_table("login_attempt")
    op.drop_table("password_history")
    op.drop_table("social_login")
    op.drop_table("user_mfa")

    # Drop enum types
    op.execute("DROP TYPE IF EXISTS socialprovider")
    op.execute("DROP TYPE IF EXISTS mfamethod")
