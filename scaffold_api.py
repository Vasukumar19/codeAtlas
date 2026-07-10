import os

files = {
    "backend/app/schemas/__init__.py": "",
    "backend/app/schemas/repository.py": """
from pydantic import BaseModel, HttpUrl
import uuid
from typing import Optional
from app.models.enums import RepositoryStatus, JobStatus

class ImportRepositoryRequest(BaseModel):
    url: HttpUrl

class RepositoryResponse(BaseModel):
    id: uuid.UUID
    provider: str
    owner: str
    name: str
    remote_url: str
    default_branch: Optional[str]

    model_config = {"from_attributes": True}

class RepositoryStatusResponse(BaseModel):
    repository_id: uuid.UUID
    version_id: Optional[uuid.UUID]
    status: RepositoryStatus
    job_id: Optional[uuid.UUID]
    job_status: Optional[JobStatus]
    
    model_config = {"from_attributes": True}
""",
    "backend/app/api/endpoints/repositories.py": """
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.schemas.repository import ImportRepositoryRequest, RepositoryResponse, RepositoryStatusResponse
from app.services.repository_service import RepositoryService
from app.core.executor import LocalBackgroundExecutor
from app.models import Repository, RepositoryVersion, Job

router = APIRouter()

def get_repository_service(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    executor = LocalBackgroundExecutor(background_tasks)
    return RepositoryService(db, executor)

@router.post("/import", status_code=202)
async def import_repository(
    request: ImportRepositoryRequest,
    service: RepositoryService = Depends(get_repository_service)
):
    try:
        job_id = await service.queue_import(str(request.url))
        return {"job_id": job_id, "message": "Import job queued"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=list[RepositoryResponse])
async def list_repositories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repository))
    return result.scalars().all()

@router.get("/{id}", response_model=RepositoryResponse)
async def get_repository(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repository).filter(Repository.id == id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return repo

@router.get("/{id}/status", response_model=RepositoryStatusResponse)
async def get_repository_status(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RepositoryVersion, Job)
        .join(Job, Job.repository_version_id == RepositoryVersion.id)
        .filter(RepositoryVersion.repository_id == id)
        .order_by(RepositoryVersion.created_at.desc())
        .limit(1)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Status not found for repository")
    version, job = row
    return RepositoryStatusResponse(
        repository_id=id,
        version_id=version.id,
        status=version.status,
        job_id=job.id,
        job_status=job.status
    )

@router.post("/{id}/refresh", status_code=202)
async def refresh_repository(
    id: uuid.UUID,
    service: RepositoryService = Depends(get_repository_service)
):
    # For now just stubbing as per Milestone 2 requirements
    raise HTTPException(status_code=501, detail="Refresh not fully implemented in Milestone 2")

@router.delete("/{id}", status_code=204)
async def delete_repository(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repository).filter(Repository.id == id))
    repo = result.scalars().first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Also trigger storage provider cleanup here...
    from app.providers.storage_provider import LocalFileSystemStorageProvider
    storage = LocalFileSystemStorageProvider()
    
    # Find versions to cleanup
    ver_result = await db.execute(select(RepositoryVersion).filter(RepositoryVersion.repository_id == id))
    for ver in ver_result.scalars().all():
        if ver.clone_path:
            await storage.cleanup(ver.clone_path)
            
    await db.delete(repo)
    await db.commit()
    
    from app.core.events import event_bus
    await event_bus.publish("RepositoryDeleted", repository_id=str(id))
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
