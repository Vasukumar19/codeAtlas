import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.api.deps import get_db
from app.core.config import settings
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
async def test_get_settings_masked(client: AsyncClient):
    token = settings.admin_api_token
    headers = {"X-Admin-Token": token}
    response = await client.get("/api/v1/settings", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["embedding_provider"] == "OpenAI"
    # Secrets must be masked or empty, never raw plaintext
    assert data["gemini_api_key"] in ["", "••••••••"]
    assert data["github_token"] in ["", "••••••••"]

@pytest.mark.asyncio
async def test_update_settings_validation(client: AsyncClient):
    token = settings.admin_api_token
    headers = {"X-Admin-Token": token}
    payload = {
        "embedding_provider": "Gemini",
        "github_token": "test-token",
        "gemini_api_key": "test-key\ninjection_line=foo", # Has newline to trigger validation fail
        "openai_api_key": "test-openai"
    }
    with patch("builtins.open", mock_open()):
        response = await client.post("/api/v1/settings", json=payload, headers=headers)
        # Should reject with HTTP 400 Bad Request
        assert response.status_code == 400
        assert "Invalid characters" in response.json()["message"]

@pytest.mark.asyncio
async def test_admin_token_auth(client: AsyncClient):
    # Set an ADMIN_API_TOKEN env variable to test authentication check
    with patch.dict(os.environ, {"ADMIN_API_TOKEN": "secret-admin-pass"}):
        # 1. Unauthenticated request should return 401
        response = await client.get("/api/v1/settings")
        assert response.status_code == 401
        
        # 2. Authenticated request with correct header should succeed
        headers = {"X-Admin-Token": "secret-admin-pass"}
        response2 = await client.get("/api/v1/settings", headers=headers)
        assert response2.status_code == 200
        
        # 3. Authenticated request with wrong token should fail
        headers_wrong = {"X-Admin-Token": "wrong-pass"}
        response3 = await client.get("/api/v1/settings", headers=headers_wrong)
        assert response3.status_code == 401
