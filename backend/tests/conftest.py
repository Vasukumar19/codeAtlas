"""Shared test fixtures for the API test suite."""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.base_class import Base
from app.main import app
from app.db.session import get_session

# Override the database URL for tests
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/codeatlas_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    # Setup test db schema
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
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

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_session] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
