import asyncio

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.events import event_bus
from app.core.executor import LocalBackgroundExecutor
from app.core.logger import get_logger
from app.models import Job, Repository, RepositoryVersion
from app.models.enums import JobStatus, JobType, RepositoryStatus
from app.providers.github_provider import GitHubProvider
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

    async def queue_import(self, url: str) -> tuple[str, str]:
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
            return str(job.id), str(repo.id)
        except Exception as e:
            async with _lock:
                _import_locks.discard(remote_url)
            raise e

    @classmethod
    def release_lock(cls, remote_url: str):
        _import_locks.discard(remote_url)
