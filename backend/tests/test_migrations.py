"""Alembic at startup (plan B1, 2026-11-03): fresh, pre-Alembic and repeated runs."""
import sqlite3

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

import backend.models  # noqa: F401
from backend.database import Base
from backend.migrations_runner import upgrade_database


def _engine(path):
    return create_engine(f"sqlite:///{path}")


def test_fresh_database_matches_models(tmp_path):
    engine = _engine(tmp_path / "fresh.db")
    upgrade_database(engine)
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert [d for d in diff if d[0] in ("add_table", "remove_table", "add_column", "remove_column")] == []
    assert "alembic_version" in inspect(engine).get_table_names()


def test_pre_alembic_database_gets_missing_columns_and_keeps_rows(tmp_path):
    path = tmp_path / "old.db"
    con = sqlite3.connect(path)
    # flashcards as they looked before the 2026-09-16 FSRS columns (cve_id, stability, ...)
    con.execute("CREATE TABLE flashcards (id INTEGER PRIMARY KEY, user_id INTEGER, front TEXT, back TEXT)")
    con.execute("INSERT INTO flashcards (id, user_id, front, back) VALUES (1, 1, 'nmap -sV', 'wersje usług')")
    con.commit()
    con.close()

    engine = _engine(path)
    upgrade_database(engine)

    columns = {c["name"] for c in inspect(engine).get_columns("flashcards")}
    assert {"stability", "difficulty", "state", "card_id"} <= columns
    con = sqlite3.connect(path)
    assert con.execute("SELECT front FROM flashcards WHERE id = 1").fetchone() == ("nmap -sV",)
    con.close()


def test_upgrade_is_repeatable(tmp_path):
    engine = _engine(tmp_path / "twice.db")
    upgrade_database(engine)
    upgrade_database(engine)
    con = sqlite3.connect(tmp_path / "twice.db")
    assert con.execute("SELECT count(*) FROM alembic_version").fetchone() == (1,)
    con.close()
