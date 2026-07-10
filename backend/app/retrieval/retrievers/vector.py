import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult
from app.models.embeddings.metadata import EmbeddingMetadataModel
from app.intelligence.models.registry import ModelRegistry

class VectorRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> List[RetrievalResult]:
        provider = ModelRegistry.get("Gemini")
        if not provider:
            return []
            
        # 1. Embed query
        query_vector = await provider.embed_batch([query.query])
        if not query_vector:
            return []
            
        vector = query_vector[0]
        
        # 2. pgvector similarity search
        # pgvector uses `<=>` for cosine distance, `<#>` for inner product, `<->` for L2
        stmt = (
            select(EmbeddingMetadataModel)
            .filter(EmbeddingMetadataModel.repository_version_id == query.repository_version_id)
            .order_by(EmbeddingMetadataModel.vector.cosine_distance(vector))
            .limit(5)
        )
        
        results = (await db.execute(stmt)).scalars().all()
        
        return [
            RetrievalResult(
                node_id=r.knowledge_node_id,
                entity_type=r.structured_metadata.get("entity_type", "Unknown"),
                relevance_score=0.9, # To dynamically score, we can select the distance in the query
                evidence=["Vector semantic search match via pgvector"]
            ) for r in results
        ]
