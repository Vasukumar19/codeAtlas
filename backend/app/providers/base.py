from abc import ABC, abstractmethod
from typing import Any


class RepositoryProvider(ABC):
    @abstractmethod
    async def validate(self, url: str) -> bool:
        pass
    
    @abstractmethod
    async def normalize_identity(self, url: str) -> dict[str, str]:
        pass
    
    @abstractmethod
    async def get_metadata(self, owner: str, name: str) -> dict[str, Any]:
        pass

class GitProvider(ABC):
    @abstractmethod
    async def clone(self, remote_url: str, clone_path: str, branch: str | None = None) -> str:
        pass

class StorageProvider(ABC):
    @abstractmethod
    async def allocate_path(self, repository_id: str, version_id: str) -> str:
        pass
    
    @abstractmethod
    async def cleanup(self, path: str) -> None:
        pass
