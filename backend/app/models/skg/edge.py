
import uuid

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class SKGEdgeModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "skg_edges"
    
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    source_id: Mapped[uuid.UUID] = mapped_column(index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(index=True)
    edge_type: Mapped[str] = mapped_column(String, index=True)
    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)
    provenance: Mapped[dict] = mapped_column(JSON, default=dict)
