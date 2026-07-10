import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult
from app.models.rim.models import RIMSymbolModel

class FunctionRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> List[RetrievalResult]:
        q = query.query.lower()
        stmt = select(RIMSymbolModel).filter(
            RIMSymbolModel.repository_version_id == query.repository_version_id,
            RIMSymbolModel.symbol_type == "function",
            RIMSymbolModel.name.ilike(f"%{q}%")
        ).limit(5)
        
        results = (await db.execute(stmt)).scalars().all()
        return [
            RetrievalResult(
                node_id=r.id,
                entity_type="Function",
                relevance_score=0.8,
                evidence=[f"Matched function signature: {r.name}"]
            ) for r in results
        ]
