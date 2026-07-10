import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .repository_version import RepositoryVersion

class ParsingReport(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "parsing_reports"

    repository_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repository_versions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    parsed_files: Mapped[int] = mapped_column(default=0)
    skipped_files: Mapped[int] = mapped_column(default=0)
    unsupported_files: Mapped[int] = mapped_column(default=0)
    failed_files: Mapped[int] = mapped_column(default=0)
    
    languages_detected: Mapped[list[str]] = mapped_column(JSON, default=list)
    parse_time_ms: Mapped[int] = mapped_column(default=0)
    
    errors_count: Mapped[int] = mapped_column(default=0)
    warnings_count: Mapped[int] = mapped_column(default=0)
    
    repository_version: Mapped["RepositoryVersion"] = relationship("RepositoryVersion")
