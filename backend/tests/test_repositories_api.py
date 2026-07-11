import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

from app.api.deps import get_db

@pytest.fixture
async def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_list_repositories_empty(client: AsyncClient):
    response = await client.get("/api/v1/repositories/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_import_invalid_repository(client: AsyncClient):
    response = await client.post("/api/v1/repositories/import", json={"url": "https://gitlab.com/test/repo"})
    assert response.status_code == 400
    assert "Invalid or unsupported" in response.json()["message"]
