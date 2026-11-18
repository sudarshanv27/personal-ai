"""add user role

Revision ID: 56a2563dea12
Revises: 116c0a556a86
Create Date: 2026-09-19

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "56a2563dea12"
down_revision: Union[str, Sequence[str], None] = "116c0a556a86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=50),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE users SET role = 'user' WHERE role IS NULL"
    )

    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=50),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "role",
    )
    