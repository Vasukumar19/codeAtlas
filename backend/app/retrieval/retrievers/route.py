import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult
from app.models.rim.models import RIMRouteModel

class RouteRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> List[RetrievalResult]:
        # Search for routes matching the query in their path
        q = query.query.lower()
        stmt = select(RIMRouteModel).filter(
            RIMRouteModel.repository_version_id == query.repository_version_id,
            RIMRouteModel.path.ilike(f"%{q}%")
        ).limit(5)
        
        results = (await db.execute(stmt)).scalars().all()
        return [
            RetrievalResult(
                node_id=r.id,
                entity_type="Route",
                relevance_score=0.95,
                evidence=[f"Matched endpoint path: {r.path}"]
            ) for r in results
        ]
