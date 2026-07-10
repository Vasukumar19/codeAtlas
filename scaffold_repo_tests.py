import os

files = {
    "backend/tests/test_repositories_api.py": """
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
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
