import os

files = {
    "backend/app/models/__init__.py": """
from .repository import Repository
from .repository_version import RepositoryVersion
from .job import Job
""",
    "backend/app/models/enums.py": """
import enum

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class RepositoryStatus(str, enum.Enum):
    NEW = "NEW"
    QUEUED = "QUEUED"
    CLONING = "CLONING"
    READY_TO_PARSE = "READY_TO_PARSE"
    FAILED = "FAILED"

class JobType(str, enum.Enum):
    IMPORT = "IMPORT"
    REFRESH = "REFRESH"
""",
    "backend/app/models/repository.py": """
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from app.db.base_class import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from .repository_version import RepositoryVersion

class Repository(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "repositories"

    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    owner: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    remote_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    default_branch: Mapped[str | None] = mapped_column(String(255), nullable=True)

    versions: Mapped[list["RepositoryVersion"]] = relationship("RepositoryVersion", back_populates="repository", cascade="all, delete-orphan")
""",
    "backend/app/models/repository_version.py": """
import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Enum, ForeignKey
from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import RepositoryStatus

if TYPE_CHECKING:
    from .repository import Repository
    from .job import Job

class RepositoryVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "repository_versions"

    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    commit_hash: Mapped[str | None] = mapped_column(String(40), nullable=True)
    branch_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    clone_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    
    status: Mapped[RepositoryStatus] = mapped_column(Enum(RepositoryStatus), default=RepositoryStatus.NEW, nullable=False, index=True)
    
    rim_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    graph_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    embedding_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    repository: Mapped["Repository"] = relationship("Repository", back_populates="versions")
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="repository_version", cascade="all, delete-orphan")
""",
    "backend/app/models/job.py": """
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum, ForeignKey, Text, DateTime
from app.db.base_class import Base, UUIDMixin, TimestampMixin
from app.models.enums import JobStatus, JobType

if TYPE_CHECKING:
    from .repository_version import RepositoryVersion

class Job(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "jobs"

    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False, index=True)
    repository_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("repository_versions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    type: Mapped[JobType] = mapped_column(Enum(JobType), nullable=False)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False, index=True)
    
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    queued_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    repository_version: Mapped["RepositoryVersion"] = relationship("RepositoryVersion", back_populates="jobs")
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
