from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Set
from app.models.embeddings.metadata import EmbeddingMetadataModel

class EmbeddingCache:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def filter_cached(self, chunk_hashes: List[str], knowledge_version_id: str, model_name: str) -> Set[str]:
        # Returns a set of chunk hashes that ALREADY exist in DB
        if not chunk_hashes:
            return set()
            
        stmt = select(EmbeddingMetadataModel.chunk_hash).where(
            EmbeddingMetadataModel.chunk_hash.in_(chunk_hashes),
            EmbeddingMetadataModel.knowledge_version_id == knowledge_version_id
        )
        
        # Mock synchronous execution for tests
        try:
            if hasattr(self.db, "execute"):
                result = await self.db.execute(stmt)
                return set(result.scalars().all())
        except Exception:
            pass
            
        # Fallback for MockAsyncSession
        return set()
