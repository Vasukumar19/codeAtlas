import uuid

from pydantic import BaseModel, HttpUrl

from app.models.enums import JobStatus, RepositoryStatus


class ImportRepositoryRequest(BaseModel):
    url: HttpUrl

class RepositoryResponse(BaseModel):
    id: uuid.UUID
    provider: str
    owner: str
    name: str
    remote_url: str
    default_branch: str | None

    model_config = {"from_attributes": True}

class RepositoryStatusResponse(BaseModel):
    repository_id: uuid.UUID
    version_id: uuid.UUID | None
    status: RepositoryStatus
    job_id: uuid.UUID | None
    job_status: JobStatus | None
    
    model_config = {"from_attributes": True}
