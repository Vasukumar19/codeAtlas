import os

files = {
    "backend/app/providers/__init__.py": "",
    "backend/app/providers/base.py": """
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class RepositoryProvider(ABC):
    @abstractmethod
    async def validate(self, url: str) -> bool:
        pass
    
    @abstractmethod
    async def normalize_identity(self, url: str) -> Dict[str, str]:
        pass
    
    @abstractmethod
    async def get_metadata(self, owner: str, name: str) -> Dict[str, Any]:
        pass

class GitProvider(ABC):
    @abstractmethod
    async def clone(self, remote_url: str, clone_path: str, branch: Optional[str] = None) -> str:
        pass

class StorageProvider(ABC):
    @abstractmethod
    async def allocate_path(self, repository_id: str, version_id: str) -> str:
        pass
    
    @abstractmethod
    async def cleanup(self, path: str) -> None:
        pass
""",
    "backend/app/providers/storage_provider.py": """
import os
import shutil
from pathlib import Path
from app.providers.base import StorageProvider
from app.core.logger import get_logger

logger = get_logger(__name__)

class LocalFileSystemStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = "data/repos"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def allocate_path(self, repository_id: str, version_id: str) -> str:
        path = self.base_dir / str(repository_id) / str(version_id) / "source"
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    async def cleanup(self, path: str) -> None:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            logger.info("Cleaned up path", path=path)
""",
    "backend/app/providers/github_provider.py": """
import httpx
from typing import Dict, Any
from app.providers.base import RepositoryProvider
from app.core.logger import get_logger

logger = get_logger(__name__)

class GitHubProvider(RepositoryProvider):
    def __init__(self, token: str | None = None):
        self.token = token
        self.base_url = "https://api.github.com"
        
    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    async def normalize_identity(self, url: str) -> Dict[str, str]:
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

    async def get_metadata(self, owner: str, name: str) -> Dict[str, Any]:
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
""",
    "backend/app/providers/git_provider.py": """
import asyncio
from typing import Optional
from git import Repo
from app.providers.base import GitProvider
from app.core.logger import get_logger

logger = get_logger(__name__)

class GitPythonProvider(GitProvider):
    async def clone(self, remote_url: str, clone_path: str, branch: Optional[str] = None) -> str:
        logger.info("Starting git clone", remote_url=remote_url, clone_path=clone_path, branch=branch)
        def _clone():
            kwargs = {"depth": 1}
            if branch:
                kwargs["branch"] = branch
            repo = Repo.clone_from(remote_url, clone_path, **kwargs)
            return repo.head.commit.hexsha

        loop = asyncio.get_event_loop()
        commit_hash = await loop.run_in_executor(None, _clone)
        logger.info("Clone complete", commit_hash=commit_hash)
        return commit_hash
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
