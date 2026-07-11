import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin, UUIDMixin

class ConversationSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversation_sessions"

    repository_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("repositories.id"), nullable=False, index=True)
    history: Mapped[list[dict]] = mapped_column(JSON, default=list, nullable=False)
    selected_graph_node: Mapped[str | None] = mapped_column(String(255), nullable=True)
    active_filters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
