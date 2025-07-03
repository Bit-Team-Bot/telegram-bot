"""add id column to groups table

Revision ID: 30ea80dfc535
Revises: 
Create Date: 2025-07-02 23:06:55.885984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30ea80dfc535'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('groups', sa.Column('id', sa.Integer(), autoincrement=True))
    # id als neuen Primärschlüssel setzen ist mit SQLite nicht direkt möglich, aber für ForeignKeys reicht die Spalte
    # Optional: Bestehende Einträge mit Werten füllen
    op.execute('UPDATE groups SET id = group_id')
    # Index auf id-Spalte
    op.create_index('ix_groups_id', 'groups', ['id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_groups_id', table_name='groups')
    op.drop_column('groups', 'id')
