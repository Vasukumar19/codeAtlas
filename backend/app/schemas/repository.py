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
