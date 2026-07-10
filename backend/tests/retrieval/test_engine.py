import pytest
import uuid
from app.retrieval.domain.schemas import UserQuery, RetrievalIntent
from app.retrieval.engine import HybridRetrievalEngine
from app.retrieval.registry import RetrievalRegistry
from app.retrieval.retrievers.graph import GraphRetriever
from app.retrieval.retrievers.route import RouteRetriever
from app.retrieval.retrievers.vector import VectorRetriever
from app.retrieval.retrievers.metadata import MetadataRetriever
from app.retrieval.retrievers.function import FunctionRetriever

class MockAsyncSession:
    def __init__(self):
        self.added = []
    def add(self, obj):
        self.added.append(obj)
    async def commit(self):
        pass
    async def execute(self, stmt):
        class MockResult:
            def scalars(self):
                class MockScalars:
                    def all(self):
                        return []
                return MockScalars()
        return MockResult()

@pytest.fixture(autouse=True)
def setup_registry():
    # Use mock retrievers for engine test since real ones need DB setup
    class MockGraphRetriever(GraphRetriever):
        async def retrieve(self, q, db):
            from app.retrieval.domain.schemas import RetrievalResult
            return [RetrievalResult(node_id=uuid.uuid4(), entity_type="GraphPath", relevance_score=0.9, evidence=[])]
    class MockRouteRetriever(RouteRetriever):
        async def retrieve(self, q, db):
            from app.retrieval.domain.schemas import RetrievalResult
            return [RetrievalResult(node_id=uuid.uuid4(), entity_type="Route", relevance_score=0.95, evidence=[])]
    class MockVectorRetriever(VectorRetriever):
        async def retrieve(self, q, db):
            return []
    class MockMetadataRetriever(MetadataRetriever):
        async def retrieve(self, q, db):
            return []
    class MockFunctionRetriever(FunctionRetriever):
        async def retrieve(self, q, db):
            return []

    RetrievalRegistry.register("GraphRetriever", MockGraphRetriever())
    RetrievalRegistry.register("RouteRetriever", MockRouteRetriever())
    RetrievalRegistry.register("VectorRetriever", MockVectorRetriever())
    RetrievalRegistry.register("MetadataRetriever", MockMetadataRetriever())
    RetrievalRegistry.register("FunctionRetriever", MockFunctionRetriever())

@pytest.mark.asyncio
async def test_hybrid_retrieval_engine():
    db = MockAsyncSession()
    engine = HybridRetrievalEngine(db)
    
    # Test Impact Analysis Query
    query1 = UserQuery(
        query="What breaks if I remove JWT middleware?",
        repository_id=uuid.uuid4(),
        repository_version_id=uuid.uuid4()
    )
    
    package1 = await engine.retrieve(query1)
    
    assert db.added[0].intent == RetrievalIntent.IMPACT_ANALYSIS.value
    assert "GraphRetriever" in db.added[0].plan["retrievers"]
    assert "GraphPath" in [r.entity_type for r in package1.relevant_entities] + ["GraphPath" if package1.relevant_graph_paths else ""]
    
    # Test Execution Flow Query
    query2 = UserQuery(
        query="How does the login flow work?",
        repository_id=uuid.uuid4(),
        repository_version_id=uuid.uuid4()
    )
    
    package2 = await engine.retrieve(query2)
    
    assert db.added[1].intent == RetrievalIntent.EXECUTION_FLOW.value
    assert "RouteRetriever" in db.added[1].plan["retrievers"]
    assert len(package2.relevant_routes) > 0
    
    # Test Validation Failure (Empty results mock)
    # If a query returns no results, the validator should reject it.
    class EmptyRetriever(VectorRetriever):
        async def retrieve(self, q, db): return []
        
    RetrievalRegistry.register("VectorRetriever", EmptyRetriever())
    RetrievalRegistry.register("DocumentationRetriever", EmptyRetriever())
    RetrievalRegistry.register("MetadataRetriever", EmptyRetriever())
    
    query3 = UserQuery(
        query="Random text that triggers GENERAL_QUESTION.",
        repository_id=uuid.uuid4(),
        repository_version_id=uuid.uuid4()
    )
    
    package3 = await engine.retrieve(query3)
    # Because retrievers returned empty, validation fails and returns empty ContextPackage
    assert len(package3.relevant_entities) == 0
    assert len(package3.relevant_routes) == 0
