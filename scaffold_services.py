import os

files = {
    "backend/app/services/__init__.py": "",
    "backend/app/services/repository_service.py": """
import asyncio
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models import Repository, RepositoryVersion, Job
from app.models.enums import JobType, JobStatus, RepositoryStatus
from app.providers.github_provider import GitHubProvider
from app.core.executor import LocalBackgroundExecutor
from app.core.logger import get_logger
from app.core.events import event_bus
from app.services.import_service import execute_import_job

logger = get_logger(__name__)

# In-memory lock to prevent duplicate concurrent imports
_import_locks = set()
_lock = asyncio.Lock()

class RepositoryService:
    def __init__(self, db: AsyncSession, executor: LocalBackgroundExecutor):
        self.db = db
        self.executor = executor
        self.github = GitHubProvider()

    async def get_or_create_repository(self, url: str) -> tuple[Repository, bool]:
        if not await self.github.validate(url):
            raise HTTPException(status_code=400, detail="Invalid or unsupported repository URL")

        identity = await self.github.normalize_identity(url)
        remote_url = identity["remote_url"]

        result = await self.db.execute(select(Repository).filter(Repository.remote_url == remote_url))
        repo = result.scalars().first()

        if repo:
            return repo, False

        metadata = await self.github.get_metadata(identity["owner"], identity["name"])

        repo = Repository(
            provider=identity["provider"],
            owner=identity["owner"],
            name=identity["name"],
            remote_url=remote_url,
            default_branch=metadata.get("default_branch")
        )
        self.db.add(repo)
        await self.db.commit()
        await self.db.refresh(repo)
        return repo, True

    async def queue_import(self, url: str) -> str:
        identity = await self.github.normalize_identity(url)
        remote_url = identity["remote_url"]
        
        async with _lock:
            if remote_url in _import_locks:
                raise HTTPException(status_code=409, detail="Repository import is already in progress")
            _import_locks.add(remote_url)

        try:
            repo, _ = await self.get_or_create_repository(url)
            
            # Create a new version
            version = RepositoryVersion(repository_id=repo.id, status=RepositoryStatus.NEW)
            self.db.add(version)
            await self.db.commit()
            await self.db.refresh(version)

            job = Job(
                repository_id=repo.id,
                repository_version_id=version.id,
                type=JobType.IMPORT,
                status=JobStatus.QUEUED
            )
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)

            logger.info("Queued import job", job_id=str(job.id), repository_id=str(repo.id))
            await event_bus.publish("RepositoryQueued", repository_id=str(repo.id))
            
            self.executor.submit(execute_import_job, job.id, repo.remote_url)
            return str(job.id)
        except Exception as e:
            async with _lock:
                _import_locks.discard(remote_url)
            raise e

    @classmethod
    def release_lock(cls, remote_url: str):
        _import_locks.discard(remote_url)
""",
    "backend/app/services/import_service.py": """
import asyncio
from datetime import datetime, timezone
from app.db.session import AsyncSessionLocal
from sqlalchemy import select
from app.models import Job, RepositoryVersion
from app.models.enums import JobStatus, RepositoryStatus
from app.providers.git_provider import GitPythonProvider
from app.providers.storage_provider import LocalFileSystemStorageProvider
from app.core.logger import get_logger
from app.core.events import event_bus

logger = get_logger(__name__)

async def execute_import_job(job_id: str, remote_url: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Job).filter(Job.id == job_id))
        job = result.scalars().first()
        if not job:
            return

        result = await db.execute(select(RepositoryVersion).filter(RepositoryVersion.id == job.repository_version_id))
        version = result.scalars().first()

        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(timezone.utc)
        version.status = RepositoryStatus.CLONING
        await db.commit()

        await event_bus.publish("RepositoryCloning", repository_id=str(job.repository_id))

        try:
            storage = LocalFileSystemStorageProvider()
            clone_path = await storage.allocate_path(str(job.repository_id), str(version.id))
            
            git = GitPythonProvider()
            commit_hash = await git.clone(remote_url, clone_path)

            version.commit_hash = commit_hash
            version.clone_path = clone_path
            version.status = RepositoryStatus.READY_TO_PARSE
            job.status = JobStatus.SUCCESS
            job.completed_at = datetime.now(timezone.utc)
            
            await db.commit()
            
            await event_bus.publish("RepositoryImported", repository_id=str(job.repository_id), version_id=str(version.id))
            logger.info("Import job completed successfully", job_id=str(job.id))

        except Exception as e:
            logger.error("Import job failed", job_id=str(job.id), error=str(e))
            version.status = RepositoryStatus.FAILED
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            await event_bus.publish("RepositoryImportFailed", repository_id=str(job.repository_id))
        finally:
            from app.services.repository_service import RepositoryService
            RepositoryService.release_lock(remote_url)
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
