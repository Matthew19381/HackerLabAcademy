"""topics.practice_hint from the old DVWA lab_type (plan C3, decision 4 of 2026-08-09).

lab_type stays (historical data is kept); practice_hint is the TryHackMe search phrase the
Practice page links to.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

HINTS = {
    "dvwa_sqli": "SQL Injection",
    "dvwa_xss_reflected": "Cross-site Scripting",
    "dvwa_brute_force": "Hydra",
    "dvwa_csrf": "CSRF",
    "dvwa_idor": "IDOR",
    "dvwa_file_upload": "Upload Vulnerabilities",
    "dvwa_command_injection": "Command Injection",
    "dvwa_sqli_blind": "SQL Injection",
    "dvwa_xss_stored": "Cross-site Scripting",
    "dvwa_file_inclusion": "File Inclusion",
}


def upgrade() -> None:
    bind = op.get_bind()
    columns = {c["name"] for c in sa.inspect(bind).get_columns("topics")}
    if "practice_hint" not in columns:
        with op.batch_alter_table("topics") as batch_op:
            batch_op.add_column(sa.Column("practice_hint", sa.String(), nullable=True))
    for lab_type, hint in HINTS.items():
        bind.execute(
            sa.text("UPDATE topics SET practice_hint = :hint WHERE lab_type = :lab AND practice_hint IS NULL"),
            {"hint": hint, "lab": lab_type},
        )


def downgrade() -> None:
    with op.batch_alter_table("topics") as batch_op:
        batch_op.drop_column("practice_hint")
