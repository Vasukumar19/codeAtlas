import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class EmbeddingMetadataModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embedding_metadata"
    
    collection_id: Mapped[uuid.UUID] = mapped_column(index=True)
    knowledge_node_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    knowledge_version_id: Mapped[str] = mapped_column(String, index=True)
    
    chunk_hash: Mapped[str] = mapped_column(String, index=True)
    vector_id: Mapped[str] = mapped_column(String, index=True)
    
    structured_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
