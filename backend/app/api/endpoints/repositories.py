import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.schemas.repository import ImportRepositoryRequest, RepositoryResponse, RepositoryStatusResponse
from app.services.repository_service import RepositoryService
from app.core.executor import LocalBackgroundExecutor
from app.models import Repository, RepositoryVersion, Job, ParsingReport
from sqlalchemy import func

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
        job_id, repo_id = await service.queue_import(str(request.url))
        return {"job_id": job_id, "repository_id": repo_id, "message": "Import job queued"}
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

@router.get("/{id}/stats")
async def get_repository_stats(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Simple real stats based on the parsed version
    result = await db.execute(
        select(RepositoryVersion)
        .filter(RepositoryVersion.repository_id == id)
        .order_by(RepositoryVersion.created_at.desc())
        .limit(1)
    )
    version = result.scalars().first()
    if not version:
        raise HTTPException(status_code=404, detail="No versions found")
    report_res = await db.execute(
        select(ParsingReport)
        .filter(ParsingReport.repository_version_id == version.id)
        .order_by(ParsingReport.created_at.desc())
        .limit(1)
    )
    report = report_res.scalars().first()
    
    score = "A+"
    tech_debt = "Low"
    knowledge_coverage = "0%"
    graph_density = "Low"
    
    if report:
        if report.errors_count == 0:
            score = "A+"
            tech_debt = "Low"
        elif report.errors_count < 10:
            score = "A"
            tech_debt = "Medium"
        else:
            score = "C"
            tech_debt = "High"
            
        total_files = report.parsed_files + report.skipped_files + report.unsupported_files + report.failed_files
        if total_files > 0:
            coverage = int((report.parsed_files / total_files) * 100)
            knowledge_coverage = f"{coverage}%"
            
        if report.parsed_files > 50:
            graph_density = "High"
        elif report.parsed_files > 10:
            graph_density = "Medium"

    return {
        "score": score,
        "technicalDebt": tech_debt, 
        "knowledgeCoverage": knowledge_coverage,
        "graphDensity": graph_density
    }

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
