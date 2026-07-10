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
