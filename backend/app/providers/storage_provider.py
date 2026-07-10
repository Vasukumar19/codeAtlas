import os
import shutil
from pathlib import Path

from app.core.logger import get_logger
from app.providers.base import StorageProvider

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
