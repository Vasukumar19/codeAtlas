import pytest
import uuid
from app.embeddings.orchestrator import EmbeddingOrchestrator
from app.embeddings.providers.sentence_transformer import SentenceTransformerProvider
from app.embeddings.store.faiss_store import FaissStore
from app.enrichment.domain.schemas import KnowledgeNode, KnowledgeIdentity, KnowledgeSemantics, KnowledgeMetadata, KnowledgeRelationships
from typing import List

class MockAsyncSession:
    def __init__(self):
        self.added = []
    def add(self, obj):
        self.added.append(obj)
    async def commit(self):
        pass

@pytest.mark.asyncio
async def test_embedding_orchestrator():
    db = MockAsyncSession()
    provider = SentenceTransformerProvider()
    store = FaissStore("test_collection", provider.dimension)
    collection_id = uuid.uuid4()
    
    orchestrator = EmbeddingOrchestrator(db, provider, store, collection_id)
    
    # 1. Create Mock Knowledge Node
    node_id = uuid.uuid4()
    version_id = uuid.uuid4()
    
    identity = KnowledgeIdentity(
        id=node_id,
        entity_type="Route",
        repository_id=uuid.uuid4(),
        repository_version_id=version_id,
        rim_entity_id=uuid.uuid4(),
        skg_node_id=uuid.uuid4()
    )
    
    node = KnowledgeNode(
        identity=identity,
        semantics=KnowledgeSemantics(
            summary=("Endpoint for authentication.", 0.9),
            purposes=[("Authentication", 0.9)]
        ),
        metadata=KnowledgeMetadata(
            layer=("Controller", 0.9),
            framework=("FastAPI", 0.9)
        ),
        relationships=KnowledgeRelationships(
            dependencies=[("Uses JWT", 0.8)]
        )
    )
    
    # Process
    k_version_id = "kv_1.0"
    embedded_count = await orchestrator.process_nodes([node], k_version_id)
    
    assert embedded_count == 1
    assert len(db.added) == 1
    
    meta = db.added[0]
    assert meta.knowledge_node_id == node_id
    assert meta.knowledge_version_id == k_version_id
    assert meta.structured_metadata["entity_type"] == "Route"
    assert meta.structured_metadata["framework"] == "FastAPI"
    assert "engine_version" in meta.provenance
    assert meta.provenance["model"] == "all-MiniLM-L6-v2"
    assert meta.provenance["provider"] == "SentenceTransformerProvider"
    
    from app.embeddings.chunker import ChunkBuilder
    chunk = ChunkBuilder.build(node, k_version_id)
    h = ChunkBuilder.compute_hash(chunk)
    
    async def mock_filter_cached(hashes, *args):
        return {h}
        
    orchestrator.cache.filter_cached = mock_filter_cached
    
    embedded_count_2 = await orchestrator.process_nodes([node], k_version_id)
    
    # Cache hit!
    assert embedded_count_2 == 0
    
    # Try invalid node (e.g. Variable)
    identity_invalid = KnowledgeIdentity(
        id=uuid.uuid4(),
        entity_type="Variable",
        repository_id=uuid.uuid4(),
        repository_version_id=version_id,
        rim_entity_id=uuid.uuid4(),
        skg_node_id=uuid.uuid4()
    )
    node_invalid = KnowledgeNode(identity=identity_invalid)
    embedded_count_3 = await orchestrator.process_nodes([node_invalid], k_version_id)
    
    # Validator rejects Variable
    assert embedded_count_3 == 0

    # Try empty summary
    identity_empty = KnowledgeIdentity(
        id=uuid.uuid4(),
        entity_type="Route",
        repository_id=uuid.uuid4(),
        repository_version_id=version_id,
        rim_entity_id=uuid.uuid4(),
        skg_node_id=uuid.uuid4()
    )
    node_empty = KnowledgeNode(identity=identity_empty)
    embedded_count_4 = await orchestrator.process_nodes([node_empty], k_version_id)
    
    # Validator rejects missing summary / text too short
    assert embedded_count_4 == 0
