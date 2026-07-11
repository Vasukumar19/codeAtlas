import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.intelligence.domain.schemas import StructuredAIResponse
from app.intelligence.gateway import AIGateway
from app.intelligence.session.manager import ConversationManager
from app.models import RepositoryVersion
from app.models.session import ConversationSession
from app.retrieval.domain.schemas import UserQuery
from app.retrieval.engine import HybridRetrievalEngine

router = APIRouter()

class AskAIRequest(BaseModel):
    query: str
    repository_id: uuid.UUID
    session_id: uuid.UUID | None = None

class UpdateSessionRequest(BaseModel):
    selected_graph_node: str | None = None
    active_filters: dict | None = None

@router.post("/ask", response_model=StructuredAIResponse)
async def ask_ai(request: AskAIRequest, db: AsyncSession = Depends(get_db)):
    # Get latest parsed repository version
    result = await db.execute(
        select(RepositoryVersion)
        .filter(RepositoryVersion.repository_id == request.repository_id)
        .order_by(RepositoryVersion.created_at.desc())
        .limit(1)
    )
    version = result.scalars().first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Repository version not found")
        
    user_query = UserQuery(
        query=request.query,
        repository_id=request.repository_id,
        repository_version_id=version.id
    )
    
    engine = HybridRetrievalEngine(db)
    context_package = await engine.retrieve(user_query)
    
    session_mgr = ConversationManager(db, request.session_id)
    await session_mgr.load_or_create(request.repository_id)
    
    gateway = AIGateway(session_mgr)
    intent = await engine.detector.detect(user_query)
    
    try:
        response = await gateway.process(
            query=request.query,
            context=context_package,
            intent=intent,
            repository_id=request.repository_id
        )
        response.session_id = session_mgr.session_id
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", response_model=list[dict])
async def list_sessions(repository_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ConversationSession)
        .filter(ConversationSession.repository_id == repository_id)
        .order_by(ConversationSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "repository_id": s.repository_id,
            "updated_at": s.updated_at,
            "history_turns_count": len(s.history),
            "selected_graph_node": s.selected_graph_node,
            "active_filters": s.active_filters
        }
        for s in sessions
    ]

@router.get("/sessions/{session_id}", response_model=dict)
async def get_session_detail(session_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ConversationSession).filter(ConversationSession.id == session_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "id": session.id,
        "repository_id": session.repository_id,
        "history": session.history,
        "selected_graph_node": session.selected_graph_node,
        "active_filters": session.active_filters,
        "updated_at": session.updated_at
    }

@router.put("/sessions/{session_id}", response_model=dict)
async def update_session(session_id: uuid.UUID, request: UpdateSessionRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ConversationSession).filter(ConversationSession.id == session_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if request.selected_graph_node is not None:
        session.selected_graph_node = request.selected_graph_node
    if request.active_filters is not None:
        session.active_filters = request.active_filters
    db.add(session)
    await db.commit()
    return {"status": "success"}
