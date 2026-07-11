"""Shared test fixtures for the API test suite."""
import json
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.core.config import settings

# WARNING/NOTE on SQLite Test Shim:
# We monkey-patch pgvector.sqlalchemy.Vector to SQLiteVector (which serializes as JSON/Text)
# so that the test suite runs database-independently without requiring Docker/PostgreSQL.
# However, this means SQLite cannot run real pgvector similarity operators like `.cosine_distance()`.
# If you write tests executing vector similarity queries, they must be run against a real Postgres
# service rather than this in-memory SQLite shim.
from sqlalchemy import Text, TypeDecorator

class SQLiteVector(TypeDecorator):
    impl = Text
    cache_ok = True
    
    def __init__(self, dim=None):
        super().__init__()
        self.dim = dim
        
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(list(value))
        return None
        
    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None

# Monkey patch pgvector.sqlalchemy.Vector before loading models
import pgvector.sqlalchemy
pgvector.sqlalchemy.Vector = SQLiteVector

from app.db.base_class import Base
from app.main import app
from app.db.session import get_session

# Override the database URL for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    # Setup test db schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session

from app.api.deps import get_db

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
