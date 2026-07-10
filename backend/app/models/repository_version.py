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
