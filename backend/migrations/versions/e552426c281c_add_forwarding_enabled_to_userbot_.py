"""Add forwarding_enabled to userbot_sessions and create forwarding_group_mappings table

Revision ID: e552426c281c
Revises: 2396441128f6
Create Date: 2025-07-03 23:26:45.607944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e552426c281c'
down_revision: Union[str, Sequence[str], None] = '2396441128f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('userbot_sessions', sa.Column('forwarding_enabled', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table(
        'forwarding_group_mappings',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('userbot_session_id', sa.Integer(), sa.ForeignKey('userbot_sessions.id')),
        sa.Column('source_group_id', sa.String(), nullable=False),
        sa.Column('target_group_id', sa.String(), nullable=False),
        sa.Column('forwarding_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(DATETIME(CURRENT_TIMESTAMP))')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(DATETIME(CURRENT_TIMESTAMP))'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('forwarding_group_mappings')
    op.drop_column('userbot_sessions', 'forwarding_enabled')
