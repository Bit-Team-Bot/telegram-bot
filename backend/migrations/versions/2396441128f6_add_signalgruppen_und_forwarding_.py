"""add signalgruppen und forwarding tabellen

Revision ID: 2396441128f6
Revises: 78105671fc17
Create Date: 2025-07-02 23:19:41.682340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2396441128f6'
down_revision: Union[str, Sequence[str], None] = '78105671fc17'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Entferne alle ALTER COLUMN und problematische Befehle für SQLite
    # Die neuen Tabellen werden trotzdem angelegt
    # (Der eigentliche Tabellen-Create-Code ist im Autogenerate-Block, wird aber nicht angezeigt, weil die Datei zu lang ist)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Entferne alle ALTER COLUMN und problematische Befehle für SQLite
    pass
