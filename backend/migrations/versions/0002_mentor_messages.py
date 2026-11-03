"""AI Mentor conversations in the database (plan B3).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "mentor_messages" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "mentor_messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mentor_messages_id", "mentor_messages", ["id"])
    op.create_index("ix_mentor_messages_session_id", "mentor_messages", ["session_id"])


def downgrade() -> None:
    op.drop_table("mentor_messages")
