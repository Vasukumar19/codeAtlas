from datetime import datetime

from sqlalchemy import select

from app.core.events import event_bus
from app.core.logger import get_logger
from app.db.session import SessionLocal
from app.models import Job, RepositoryVersion
from app.models.enums import JobStatus, RepositoryStatus
from app.providers.git_provider import GitPythonProvider
from app.providers.storage_provider import LocalFileSystemStorageProvider
from app.services.parsing_orchestrator import ParsingOrchestrator

logger = get_logger(__name__)

async def execute_import_job(job_id: str, remote_url: str):
    async with SessionLocal() as db:
        result = await db.execute(select(Job).filter(Job.id == job_id))
        job = result.scalars().first()
        if not job:
            return

        result = await db.execute(select(RepositoryVersion).filter(RepositoryVersion.id == job.repository_version_id))
        version = result.scalars().first()

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        version.status = RepositoryStatus.CLONING
        await db.commit()

        await event_bus.publish("RepositoryCloning", repository_id=str(job.repository_id))

        try:
            git = GitPythonProvider()
            commit_hash = await git.get_remote_hash(remote_url)
            
            # Check if this hash is already parsed for this repo
            existing_version = await db.execute(
                select(RepositoryVersion)
                .filter(RepositoryVersion.repository_id == job.repository_id)
                .filter(RepositoryVersion.commit_hash == commit_hash)
                .filter(RepositoryVersion.status == RepositoryStatus.PARSED)
            )
            if existing_version.scalars().first():
                logger.info("Repository version already exists, skipping clone", commit_hash=commit_hash)
                version.commit_hash = commit_hash
                version.status = RepositoryStatus.PARSED
                job.status = JobStatus.SUCCESS
                job.completed_at = datetime.utcnow()
                await db.commit()
                await event_bus.publish("RepositoryImported", repository_id=str(job.repository_id), version_id=str(version.id))
                return

            storage = LocalFileSystemStorageProvider()
            clone_path = await storage.allocate_path(str(job.repository_id), str(version.id))
            
            commit_hash = await git.clone(remote_url, clone_path)

            version.commit_hash = commit_hash
            version.clone_path = clone_path
            version.status = RepositoryStatus.READY_TO_PARSE
            job.status = JobStatus.SUCCESS
            job.completed_at = datetime.utcnow()
            
            await db.commit()
            
            await event_bus.publish("RepositoryImported", repository_id=str(job.repository_id), version_id=str(version.id))
            logger.info("Import job completed successfully", job_id=str(job.id))
            
            # Immediately trigger parsing to complete the pipeline in background
            logger.info("Triggering parsing orchestrator", version_id=str(version.id))
            orchestrator = ParsingOrchestrator(db)
            await orchestrator.parse_repository_version(str(version.id))

        except Exception as e:
            logger.error("Import job failed", job_id=str(job.id), error=str(e))
            version.status = RepositoryStatus.FAILED
            job.status = JobStatus.FAILED
            job.error = str(e)
            job.completed_at = datetime.utcnow()
            await db.commit()
            await event_bus.publish("RepositoryImportFailed", repository_id=str(job.repository_id))
        finally:
            from app.services.repository_service import RepositoryService
            RepositoryService.release_lock(remote_url)
