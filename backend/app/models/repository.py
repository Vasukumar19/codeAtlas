from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin, UUIDMixin

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
