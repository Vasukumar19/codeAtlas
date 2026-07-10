from typing import Any

import httpx

from app.core.logger import get_logger
from app.providers.base import RepositoryProvider

logger = get_logger(__name__)

class GitHubProvider(RepositoryProvider):
    def __init__(self, token: str | None = None):
        self.token = token
        self.base_url = "https://api.github.com"
        
    def _get_headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    async def normalize_identity(self, url: str) -> dict[str, str]:
        # Simple normalization: extract owner/name
        url = url.replace("git@github.com:", "https://github.com/")
        if url.endswith(".git"):
            url = url[:-4]
        
        parts = url.rstrip("/").split("/")
        name = parts[-1]
        owner = parts[-2]
        return {
            "provider": "github",
            "owner": owner,
            "name": name,
            "remote_url": f"https://github.com/{owner}/{name}.git"
        }

    async def validate(self, url: str) -> bool:
        if "github.com" not in url:
            return False
        identity = await self.normalize_identity(url)
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{identity['owner']}/{identity['name']}",
                headers=self._get_headers()
            )
            return response.status_code == 200

    async def get_metadata(self, owner: str, name: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/repos/{owner}/{name}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            return {
                "default_branch": data.get("default_branch"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "topics": data.get("topics", [])
            }
