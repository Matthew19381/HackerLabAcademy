"""Alembic environment: the same database URL and metadata as the app (backend/database.py)."""
from alembic import context
from sqlalchemy import engine_from_config, pool

import backend.models  # noqa: F401  (registers every table on Base.metadata)
from backend.database import SQLALCHEMY_DATABASE_URL, Base

config = context.config
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=SQLALCHEMY_DATABASE_URL, target_metadata=target_metadata,
                      literal_binds=True, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = config.attributes.get("connection")
    if connectable is not None:  # connection handed over by migrations_runner (tests, app)
        context.configure(connection=connectable, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = engine_from_config({"sqlalchemy.url": SQLALCHEMY_DATABASE_URL}, prefix="sqlalchemy.",
                                poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
