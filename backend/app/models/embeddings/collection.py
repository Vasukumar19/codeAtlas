from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin


class EmbeddingCollectionModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "embedding_collections"
    
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    embedding_model: Mapped[str] = mapped_column(String)
    dimension: Mapped[int] = mapped_column(Integer)
    vector_store: Mapped[str] = mapped_column(String)
