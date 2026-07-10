import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_list_repositories_empty(client: AsyncClient):
    response = await client.get("/api/v1/repositories/")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_import_invalid_repository(client: AsyncClient):
    response = await client.post("/api/v1/repositories/import", json={"url": "https://gitlab.com/test/repo"})
    assert response.status_code == 400
    assert "Invalid or unsupported" in response.json()["detail"]
