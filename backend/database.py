from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from pathlib import Path

# The DB lives in the project root. The old relative "./HackerLabAcademy.db" depended on
# the working directory - started from backend/ it silently used an empty file.
_DEFAULT_DB = Path(__file__).resolve().parent.parent / "HackerLabAcademy.db"
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or f"sqlite:///{_DEFAULT_DB.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
