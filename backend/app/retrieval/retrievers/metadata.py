from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rim.models import RIMSymbolModel
from app.retrieval.retrievers.base import BaseRetriever, RetrievalResult, UserQuery


class MetadataRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> list[RetrievalResult]:
        # Search for symbols matching the query
        q = query.query.lower()
        stmt = select(RIMSymbolModel).filter(
            RIMSymbolModel.repository_version_id == query.repository_version_id,
            RIMSymbolModel.name.ilike(f"%{q}%")
        ).limit(5)
        
        results = (await db.execute(stmt)).scalars().all()
        return [
            RetrievalResult(
                node_id=r.id,
                entity_type="Symbol",
                relevance_score=0.7,
                evidence=[f"Metadata exact match: {r.name}"]
            ) for r in results
        ]
