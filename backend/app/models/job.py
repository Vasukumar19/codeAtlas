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
