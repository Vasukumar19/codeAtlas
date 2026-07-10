import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class RetrievalTraceModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "retrieval_traces"
    
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    user_query: Mapped[str] = mapped_column(String)
    intent: Mapped[str] = mapped_column(String)
    plan: Mapped[dict] = mapped_column(JSON)
    execution_time_ms: Mapped[int] = mapped_column(Integer)
    final_context_hash: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
