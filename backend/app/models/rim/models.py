import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON, String
from pgvector.sqlalchemy import Vector
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class RIMDirectoryModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_directories"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(String, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rim_directories.id"))

class RIMFileModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_files"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    directory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_directories.id"))
    path: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768))

class RIMSymbolModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_symbols"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_files.id"))
    name: Mapped[str] = mapped_column(String)
    fully_qualified_name: Mapped[str] = mapped_column(String)
    symbol_type: Mapped[str] = mapped_column(String)
    parent_symbol_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rim_symbols.id"))
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768))

class RIMImportModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_imports"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_files.id"))
    raw_statement: Mapped[str] = mapped_column(String)

class RIMRouteModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_routes"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_files.id"))
    method: Mapped[str] = mapped_column(String)
    path: Mapped[str] = mapped_column(String)
    handler: Mapped[str] = mapped_column(String)
