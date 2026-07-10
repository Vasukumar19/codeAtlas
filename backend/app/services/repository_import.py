"""Cache-aware orchestration for repository import background jobs."""

import asyncio
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.repository import (
    ImportJob,
    JobState,
    Repository,
    RepositoryState,
    RepositoryVersion,
)
from app.services.git import GitCloneError, GitService
from app.services.github import GitHubRepositoryMetadata


class RepositoryImportService:
    """Create cached imports and advance their lifecycle through clone preparation."""

    def __init__(self, session: AsyncSession, git_service: GitService | None = None) -> None:
        """Create a service with its request-scoped persistence dependency."""
        self.session = session
        self.git_service = git_service or GitService()

    async def find_cached(
        self, remote_url: str, branch: str, commit_hash: str
    ) -> Repository | None:
        """Return the ready repository that already owns the requested snapshot."""
        statement: Select[tuple[Repository]] = (
            select(Repository)
            .join(RepositoryVersion)
            .where(
                Repository.remote_url == remote_url,
                Repository.current_branch == branch,
                RepositoryVersion.commit_hash == commit_hash,
                Repository.state == RepositoryState.READY_TO_PARSE,
            )
        )
        return (await self.session.execute(statement)).scalars().first()

    async def create_import(
        self, metadata: GitHubRepositoryMetadata, branch: str
    ) -> tuple[Repository, ImportJob]:
        """Create a repository and queued job after a cache miss."""
        repository = Repository(
            provider="github",
            owner=metadata.owner,
            name=metadata.name,
            remote_url=metadata.remote_url,
            description=metadata.description,
            default_branch=metadata.default_branch,
            current_branch=branch,
            latest_commit=metadata.latest_commit,
            primary_language=metadata.primary_language,
            topics=metadata.topics,
            stars=metadata.stars,
            forks=metadata.forks,
            state=RepositoryState.QUEUED,
        )
        self.session.add(repository)
        await self.session.flush()
        job = ImportJob(repository_id=repository.id, state=JobState.QUEUED)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(repository)
        await self.session.refresh(job)
        return repository, job

    async def refresh(self, repository: Repository, branch: str) -> ImportJob:
        """Queue a new clone job for an existing repository branch."""
        repository.current_branch = branch
        repository.state = RepositoryState.QUEUED
        job = ImportJob(repository_id=repository.id, state=JobState.QUEUED)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    @staticmethod
    async def run_job(job_id: UUID) -> None:
        """Perform the clone stage in a standalone session for BackgroundTasks."""
        from app.db.session import SessionLocal

        async with SessionLocal() as session:
            job = await session.get(ImportJob, job_id)
            if job is None:
                return
            repository = await session.get(Repository, job.repository_id)
            if repository is None:
                job.state = JobState.FAILED
                job.error_message = "Repository record no longer exists."
                await session.commit()
                return
            job.state = JobState.RUNNING
            repository.state = RepositoryState.CLONING
            await session.commit()
            destination = RepositoryImportService._snapshot_path(repository, job)
            try:
                commit_hash = await asyncio.to_thread(
                    GitService().clone,
                    repository.remote_url,
                    repository.current_branch,
                    destination,
                )
                version = RepositoryVersion(
                    repository_id=repository.id,
                    commit_hash=commit_hash,
                    branch_name=repository.current_branch,
                    snapshot_path=str(destination),
                )
                session.add(version)
                await session.flush()
                repository.latest_commit = commit_hash
                repository.snapshot_path = str(destination)
                repository.clone_timestamp = datetime.now(UTC)
                repository.state = RepositoryState.READY_TO_PARSE
                job.repository_version_id = version.id
                job.state = JobState.SUCCEEDED
                await session.commit()
            except GitCloneError as error:
                shutil.rmtree(destination, ignore_errors=True)
                repository.state = RepositoryState.FAILED
                job.state = JobState.FAILED
                job.error_message = str(error)
                await session.commit()

    @staticmethod
    def _snapshot_path(repository: Repository, job: ImportJob) -> Path:
        """Build an isolated durable storage path for one clone job."""
        return (
            settings.repository_storage_path
            / repository.owner
            / repository.name
            / str(job.id)
        )
