"""migrate update users set not null

Revision ID: 1dbf84d09f53
Revises: 91dd44093fbc
Create Date: 2025-08-18 11:05:16.312546

"""
from datetime import UTC, datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1dbf84d09f53'
down_revision: Union[str, Sequence[str], None] = '91dd44093fbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Fill NULL values with safe defaults
    op.execute(
        sa.text(
            """
            UPDATE users
            SET 
                password = COALESCE(password, '$2b$12$3PQH4VXbJ1eJhSDruzQJo.rPHvVZeUax3UUxpJvTeTNUeRjbLFNhG'),
                role = COALESCE(role, 'user'),
                created_at = COALESCE(created_at, :now)
            """
        ).bindparams(now=datetime.now(UTC))
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
