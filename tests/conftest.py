import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import base configuration settings
from app.database import Base, get_db
from app.main import app

# Explicitly load model definitions to populate Base.metadata
from app.models.auth import User
from app.schemas.auth import UserRegister, TokenResponse, UserLogin 
from app.models.bookmarks import Bookmark, Tag, bookmark_tags

# Use a concrete local file for the test runtime execution to prevent connection drops
TEST_DB_FILE = "test_sandbox.db"
TEST_DB_URL = f"sqlite:///./{TEST_DB_FILE}"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def pytest_configure(config):
    """
    Executes BEFORE tests are collected. Cleans old files and safely provisions the tables.
    """
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except PermissionError:
            pass
            
    Base.metadata.create_all(bind=engine)


def pytest_unconfigure(config):
    """
    Executes AFTER all tests finish. Cleans up the test database file completely.
    """
    # Dispose of current engine connections pools to unlock the file handle
    engine.dispose()
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except PermissionError:
            pass


@pytest.fixture(scope="function")
def db_session():
    """
    Provides a isolated transaction session per test case, wiping data between assertions.
    """
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Fast truncating wipe of rows across all tables to reset testing state safely
        with engine.connect() as connection:
            trans = connection.begin()
            for table in reversed(Base.metadata.sorted_tables):
                connection.execute(table.delete())
            trans.commit()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Overrides the FastAPI database injection cleanly.
    """
    def _override_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def schema_spec():
    return app.openapi()