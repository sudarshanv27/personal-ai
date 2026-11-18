"""add unique constraint to memories

Revision ID: 73e7d869de23
Revises: 34500da52b19
Create Date: 2026-09-30
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "73e7d869de23"
down_revision: Union[str, Sequence[str], None] = "34500da52b19"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_memories_user_type_key",
        "memories",
        ["user_id", "memory_type", "key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_memories_user_type_key",
        "memories",
        type_="unique",
    )