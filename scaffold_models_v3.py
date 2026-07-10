import os

files = {
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
    PARSING = "PARSING"
    PARSED = "PARSED"
    FAILED = "FAILED"

class JobType(str, enum.Enum):
    IMPORT = "IMPORT"
    REFRESH = "REFRESH"
    PARSE = "PARSE"
""",
    "backend/app/models/parsing_report.py": """
import uuid
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON
from app.db.base_class import Base, UUIDMixin, TimestampMixin

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
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
