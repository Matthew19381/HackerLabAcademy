"""Apply Alembic migrations at startup (plan B1, 2026-11-03).

Replaces Base.metadata.create_all(): create_all never adds columns to existing tables, so every
schema change used to need a hand-written script. The baseline revision (0001) is idempotent, so a
database created before Alembic is brought up to date without losing data.
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine

ALEMBIC_INI = Path(__file__).resolve().parent / "alembic.ini"


def upgrade_database(engine: Engine) -> None:
    config = Config(str(ALEMBIC_INI))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
