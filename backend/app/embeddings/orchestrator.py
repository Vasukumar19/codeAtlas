import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.cache import EmbeddingCache
from app.embeddings.chunker import ChunkBuilder
from app.embeddings.providers.base import EmbeddingProvider
from app.enrichment.domain.schemas import KnowledgeNode
from app.models.embeddings.metadata import EmbeddingMetadataModel


class EmbeddingOrchestrator:
    def __init__(self, db: AsyncSession, collection_id: uuid.UUID):
        self.db = db
        from app.intelligence.models.registry import ModelRegistry
        self.provider = ModelRegistry.get("OpenAI")
        if not self.provider:
            from app.intelligence.models.openai import OpenAIProvider
            self.provider = OpenAIProvider()
        self.collection_id = collection_id
        self.cache = EmbeddingCache(db)
        self.engine_version = "v1.0"
        
    async def process_nodes(self, nodes: list[KnowledgeNode], knowledge_version_id: str, batch_size: int = 32) -> int:
        # 1. Build & Validate Chunks
        chunks = []
        for node in nodes:
            chunk = ChunkBuilder.build(node, knowledge_version_id)
            if chunk:
                chunks.append(chunk)
                
        if not chunks:
            return 0
            
        # 2. Check Cache
        chunk_hashes = [ChunkBuilder.compute_hash(c) for c in chunks]
        cached_hashes = await self.cache.filter_cached(chunk_hashes, knowledge_version_id, self.provider.model_name)
        
        # 3. Filter uncached
        uncached_chunks = []
        for chunk in chunks:
            h = ChunkBuilder.compute_hash(chunk)
            if h not in cached_hashes:
                uncached_chunks.append(chunk)
                
        if not uncached_chunks:
            return 0
            
        # 4. Process in Batches
        embedded_count = 0
        for i in range(0, len(uncached_chunks), batch_size):
            batch = uncached_chunks[i:i+batch_size]
            texts = [c.text for c in batch]
            
            # Embed
            vectors = await self.provider.embed_batch(texts)
            
            # Persist Metadata and Vector in PostgreSQL
            for chunk, vector in zip(batch, vectors):
                meta = EmbeddingMetadataModel(
                    id=uuid.uuid4(),
                    collection_id=self.collection_id,
                    knowledge_node_id=chunk.knowledge_node_id,
                    repository_id=chunk.repository_id,
                    repository_version_id=chunk.repository_version_id,
                    knowledge_version_id=chunk.knowledge_version_id,
                    chunk_hash=ChunkBuilder.compute_hash(chunk),
                    vector=vector,
                    structured_metadata={
                        "entity_type": chunk.entity_type,
                        "layer": chunk.layer,
                        "framework": chunk.framework,
                        "keywords": chunk.keywords
                    },
                    provenance={
                        "engine_version": self.engine_version,
                        "provider": self.provider.__class__.__name__,
                        "model": self.provider.model_name,
                        "created_at": datetime.utcnow().isoformat()
                    }
                )
                self.db.add(meta)
                embedded_count += 1
                
        await self.db.commit()
        return embedded_count
