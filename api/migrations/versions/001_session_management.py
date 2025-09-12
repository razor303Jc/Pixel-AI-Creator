"""Add session management tables

Revision ID: 001_session_management
Revises:
Create Date: 2025-09-12 07:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_session_management"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add session management tables."""

    # Create user_sessions table
    op.create_table(
        "user_sessions",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column(
            "user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True
        ),
        sa.Column("refresh_token", sa.Text, nullable=False, unique=True),
        sa.Column("status", sa.String(20), nullable=False, default="active"),
        sa.Column("session_data", sa.JSON, nullable=True),
        sa.Column("device_type", sa.String(20), default="unknown"),
        sa.Column("device_id", sa.String(255), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "last_activity",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_suspicious", sa.Boolean, default=False),
        sa.Column("login_attempts", sa.Integer, default=0),
    )

    # Create indexes for user_sessions
    op.create_index("idx_user_sessions_user_id", "user_sessions", ["user_id"])
    op.create_index("idx_user_sessions_status", "user_sessions", ["status"])
    op.create_index("idx_user_sessions_expires_at", "user_sessions", ["expires_at"])
    op.create_index("idx_user_sessions_device_id", "user_sessions", ["device_id"])

    # Create session_activities table
    op.create_table(
        "session_activities",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column(
            "session_id",
            sa.String(255),
            sa.ForeignKey("user_sessions.id"),
            nullable=False,
        ),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("endpoint", sa.String(255), nullable=True),
        sa.Column("method", sa.String(10), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("success", sa.Boolean, default=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes for session_activities
    op.create_index(
        "idx_session_activities_session_id", "session_activities", ["session_id"]
    )
    op.create_index("idx_session_activities_user_id", "session_activities", ["user_id"])
    op.create_index(
        "idx_session_activities_activity_type", "session_activities", ["activity_type"]
    )
    op.create_index(
        "idx_session_activities_timestamp", "session_activities", ["timestamp"]
    )

    # Create security_alerts table
    op.create_table(
        "security_alerts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "session_id",
            sa.String(255),
            sa.ForeignKey("user_sessions.id"),
            nullable=True,
        ),
        sa.Column("alert_type", sa.String(50), nullable=False),
        sa.Column("severity", sa.String(20), default="medium"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("metadata", sa.JSON, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("is_resolved", sa.Boolean, default=False),
        sa.Column("resolved_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Create indexes for security_alerts
    op.create_index("idx_security_alerts_user_id", "security_alerts", ["user_id"])
    op.create_index("idx_security_alerts_session_id", "security_alerts", ["session_id"])
    op.create_index("idx_security_alerts_alert_type", "security_alerts", ["alert_type"])
    op.create_index("idx_security_alerts_severity", "security_alerts", ["severity"])
    op.create_index(
        "idx_security_alerts_is_resolved", "security_alerts", ["is_resolved"]
    )
    op.create_index("idx_security_alerts_created_at", "security_alerts", ["created_at"])


def downgrade():
    """Remove session management tables."""

    # Drop tables in reverse order due to foreign key constraints
    op.drop_table("security_alerts")
    op.drop_table("session_activities")
    op.drop_table("user_sessions")
