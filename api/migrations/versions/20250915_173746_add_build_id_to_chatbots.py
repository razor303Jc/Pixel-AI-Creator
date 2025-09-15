"""Add build_id to chatbots table

Revision ID: 20250915_173746
Revises: 27928bbee94e
Create Date: 2025-09-15 17:37:46.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250915_173746'
down_revision: Union[str, Sequence[str], None] = '27928bbee94e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add build_id column to chatbots table."""
    op.add_column('chatbots', sa.Column('build_id', sa.String(255), nullable=True))


def downgrade() -> None:
    """Remove build_id column from chatbots table."""
    op.drop_column('chatbots', 'build_id')