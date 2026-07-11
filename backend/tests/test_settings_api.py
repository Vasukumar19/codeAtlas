import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_db
from unittest.mock import patch, mock_open

@pytest.fixture
async def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_settings(client: AsyncClient):
    response = await client.get("/api/v1/settings")
    assert response.status_code == 200
    data = response.json()
    assert "embedding_provider" in data
    assert "gemini_api_key" in data

@pytest.mark.asyncio
async def test_update_settings(client: AsyncClient):
    payload = {
        "embedding_provider": "Gemini",
        "github_token": "test-token",
        "gemini_api_key": "test-key",
        "openai_api_key": "test-openai"
    }
    # Mock the builtins.open only during the post call to settings to avoid writing to local workspace .env
    with patch("builtins.open", mock_open(read_data="DATABASE_URL=mock_url\n")):
        response = await client.post("/api/v1/settings", json=payload)
        assert response.status_code == 200
        assert response.json() == {"status": "success"}
