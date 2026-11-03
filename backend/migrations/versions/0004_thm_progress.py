"""TryHackMe tracker table (plan C4).

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    if "thm_progress" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "thm_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("done", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_thm_progress_id", "thm_progress", ["id"])
    op.create_index("ix_thm_progress_user_id", "thm_progress", ["user_id"])


def downgrade() -> None:
    op.drop_table("thm_progress")
