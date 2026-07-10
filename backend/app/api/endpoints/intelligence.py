import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db
from app.models import RepositoryVersion
from app.retrieval.domain.schemas import UserQuery
from app.retrieval.engine import HybridRetrievalEngine
from app.intelligence.gateway import AIGateway
from app.intelligence.domain.schemas import StructuredAIResponse
from pydantic import BaseModel

router = APIRouter()

class AskAIRequest(BaseModel):
    query: str
    repository_id: uuid.UUID
    
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
    
    gateway = AIGateway()
    # The AIGateway.process method takes: query, context, intent
    # The AIGateway.process method takes: query, context, intent
    intent = await engine.detector.detect(user_query)
    
    # We use "Gemini" by default
    try:
        response = await gateway.process(
            query=request.query,
            context=context_package,
            intent=intent
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
