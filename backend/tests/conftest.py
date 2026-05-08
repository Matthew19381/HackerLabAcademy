import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend import database as db_module
from backend.main import app

# Use temp file for test database (SQLite in-memory creates new DB per connection)
@pytest.fixture(scope="function")
def test_db_path():
    fd, path = tempfile.mkstemp(suffix=".db", prefix="test_hackerlab_")
    os.close(fd)
    yield path
    if os.path.exists(path):
        try:
            os.remove(path)
        except:
            pass


@pytest.fixture(scope="function")
def db_session(test_db_path):
    test_db_url = f"sqlite:///{test_db_path}"
    test_engine = create_engine(
        test_db_url, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Monkeypatch database module
    original_engine = db_module.engine
    original_SessionLocal = db_module.SessionLocal
    original_Base = db_module.Base

    db_module.engine = test_engine
    db_module.SessionLocal = TestingSessionLocal

    # Also monkeypatch main module
    import backend.main as main_module
    original_main_engine = main_module.engine
    original_main_SessionLocal = main_module.SessionLocal

    main_module.engine = test_engine
    main_module.SessionLocal = TestingSessionLocal

    # Import all models so Base has them registered
    from backend.models import (  # noqa
        user, topic, flashcard, flashcard_attempt, error_item,
        lab_attempt, achievement, exercise, conversation, cve,
        youtube_video, ctf, attack_scenario, defense, certificate,
        article, writeup_template
    )

    # Create tables
    db_module.Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        db_module.Base.metadata.drop_all(bind=test_engine)
        # Restore
        db_module.engine = original_engine
        db_module.SessionLocal = original_SessionLocal
        main_module.engine = original_main_engine
        main_module.SessionLocal = original_main_SessionLocal


@pytest.fixture(scope="function")
def client(db_session, test_db_path):
    def override_get_db():
        # Create a new session for each request
        from backend.database import SessionLocal
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[db_module.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
