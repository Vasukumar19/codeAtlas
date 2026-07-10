import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, String
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class KnowledgeNodeModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_nodes"
    
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    rim_entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    skg_node_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    entity_type: Mapped[str] = mapped_column(String, index=True)
    
    semantics: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    documentation: Mapped[dict] = mapped_column(JSON, default=dict)
    relationships: Mapped[dict] = mapped_column(JSON, default=dict)
    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
