import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.session import ConversationSession

class ConversationManager:
    def __init__(self, db: AsyncSession, session_id: uuid.UUID | None = None):
        self.db = db
        self.session_id = session_id
        self.session_obj: ConversationSession | None = None

    async def load_or_create(self, repository_id: uuid.UUID) -> ConversationSession:
        if self.session_id:
            result = await self.db.execute(
                select(ConversationSession).filter(ConversationSession.id == self.session_id)
            )
            self.session_obj = result.scalars().first()
            
        if not self.session_obj:
            # Create a brand new session
            self.session_obj = ConversationSession(
                repository_id=repository_id,
                history=[],
                active_filters={}
            )
            if self.session_id:
                self.session_obj.id = self.session_id
            self.db.add(self.session_obj)
            await self.db.commit()
            await self.db.refresh(self.session_obj)
            self.session_id = self.session_obj.id
            
        return self.session_obj

    async def get_history(self, repository_id: uuid.UUID) -> list[dict[str, Any]]:
        session = await self.load_or_create(repository_id)
        return session.history

    async def add_turn(self, repository_id: uuid.UUID, query: str, response: str):
        session = await self.load_or_create(repository_id)
        # Re-assign history list to ensure SQLAlchemy detects mutations
        history = list(session.history)
        history.append({"query": query, "response": response})
        session.history = history
        self.db.add(session)
        await self.db.commit()

    async def update_session_state(
        self, 
        repository_id: uuid.UUID, 
        selected_graph_node: str | None = None, 
        active_filters: dict | None = None
    ):
        session = await self.load_or_create(repository_id)
        if selected_graph_node is not None:
            session.selected_graph_node = selected_graph_node
        if active_filters is not None:
            session.active_filters = active_filters
        self.db.add(session)
        await self.db.commit()
