"""CTF restored without a leaderboard (decision 3 of 2026-08-09; removed by mistake in 1b1f2ff).

- tables: databases from before 1b1f2ff already have them (with data) - created only when missing;
- user_ctf_attempts.hint_used: the hint penalty was promised in the UI but never applied;
- the five old challenges needed the removed DVWA lab and had made-up flags (e.g. "the first line of
  /etc/passwd" = FLAG{SQL_FILE_READ}) - deactivated, their attempts stay.

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

OLD_DVWA_CHALLENGES = [
    "Flag in HTTP Headers",
    "Cookie Monster",
    "SQL Injection to Read File",
    "XSS Steal Cookie",
    "Blind Bool Time",
]


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    if "ctf_challenges" not in tables:
        op.create_table(
            "ctf_challenges",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("flag", sa.String(), nullable=False),
            sa.Column("points", sa.Integer(), nullable=True),
            sa.Column("difficulty", sa.Integer(), nullable=True),
            sa.Column("category", sa.String(), nullable=False),
            sa.Column("hint", sa.Text(), nullable=True),
            sa.Column("solution", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_ctf_challenges_id", "ctf_challenges", ["id"])
    if "user_ctf_attempts" not in tables:
        op.create_table(
            "user_ctf_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("challenge_id", sa.Integer(), nullable=False),
            sa.Column("solved", sa.Boolean(), nullable=True),
            sa.Column("solved_at", sa.DateTime(), nullable=True),
            sa.Column("attempts_count", sa.Integer(), nullable=True),
            sa.Column("points_earned", sa.Integer(), nullable=True),
            sa.Column("hint_used", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["challenge_id"], ["ctf_challenges.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_user_ctf_attempts_id", "user_ctf_attempts", ["id"])
    elif "hint_used" not in {c["name"] for c in sa.inspect(bind).get_columns("user_ctf_attempts")}:
        with op.batch_alter_table("user_ctf_attempts") as batch_op:
            batch_op.add_column(sa.Column("hint_used", sa.Boolean(), nullable=True))

    bind.execute(
        sa.text("UPDATE ctf_challenges SET is_active = 0 WHERE title IN :titles").bindparams(
            sa.bindparam("titles", expanding=True)
        ),
        {"titles": OLD_DVWA_CHALLENGES},
    )


def downgrade() -> None:
    pass  # tables existed before this revision in most databases; nothing safe to drop
