import uuid
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.enrichment.domain.schemas import KnowledgeNode
from app.embeddings.chunker import ChunkBuilder
from app.embeddings.providers.base import EmbeddingProvider
from app.embeddings.store.base import VectorStore
from app.embeddings.cache import EmbeddingCache
from app.models.embeddings.metadata import EmbeddingMetadataModel
from app.models.embeddings.collection import EmbeddingCollectionModel

class EmbeddingOrchestrator:
    def __init__(self, db: AsyncSession, provider: EmbeddingProvider, store: VectorStore, collection_id: uuid.UUID):
        self.db = db
        self.provider = provider
        self.store = store
        self.collection_id = collection_id
        self.cache = EmbeddingCache(db)
        self.engine_version = "v1.0"
        
    async def process_nodes(self, nodes: List[KnowledgeNode], knowledge_version_id: str, batch_size: int = 32) -> int:
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
            ids = [c.id for c in batch]
            
            # Store in FAISS
            self.store.add(vectors, ids)
            
            # Persist Metadata
            for chunk, vector_id in zip(batch, ids):
                meta = EmbeddingMetadataModel(
                    id=uuid.uuid4(),
                    collection_id=self.collection_id,
                    knowledge_node_id=chunk.knowledge_node_id,
                    repository_id=chunk.repository_id,
                    repository_version_id=chunk.repository_version_id,
                    knowledge_version_id=chunk.knowledge_version_id,
                    chunk_hash=ChunkBuilder.compute_hash(chunk),
                    vector_id=vector_id,
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
                
        self.store.save()
        await self.db.commit()
        return embedded_count
