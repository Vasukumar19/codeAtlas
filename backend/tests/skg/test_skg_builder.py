import pytest
import uuid
from app.skg.builder import SKGBuilder
from app.models.enums import SKGEdgeType
from app.rim.domain.models import DomainDirectory, DomainFile, DomainSymbol, DomainImport, DomainRoute

# Mock DB Session
class MockAsyncSession:
    def __init__(self):
        self.added = []
    def add(self, obj):
        self.added.append(obj)
    async def commit(self):
        pass

@pytest.mark.asyncio
async def test_skg_builder_edges():
    db = MockAsyncSession()
    version_id = uuid.uuid4()
    builder = SKGBuilder(db, version_id)
    
    # Mock RIM Objects
    d1 = DomainDirectory(id=uuid.uuid4(), repository_id=uuid.uuid4(), repository_version_id=version_id, path=".")
    f1 = DomainFile(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, path="app.py", directory_id=d1.id, language="python")
    s1 = DomainSymbol(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, file_id=f1.id, name="login", fully_qualified_name="app.py::login", symbol_type="function")
    r1 = DomainRoute(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, file_id=f1.id, method="POST", path="/login", handler="login")
    
    # Build Edges
    builder.build_structural_edges([d1], [f1], [s1])
    builder.build_route_edges([r1], [s1])
    
    await builder.commit_to_database()
    
    edges = builder.edges
    assert len(edges) == 4
    
    # Check File CONTAINS Symbol
    assert any(e.source_id == f1.id and e.target_id == s1.id and e.edge_type == SKGEdgeType.CONTAINS.value for e in edges)
    # Check Route ROUTES_TO Symbol
    assert any(e.source_id == r1.id and e.target_id == s1.id and e.edge_type == SKGEdgeType.ROUTES_TO.value for e in edges)

@pytest.mark.asyncio
async def test_skg_builder_imports():
    db = MockAsyncSession()
    version_id = uuid.uuid4()
    builder = SKGBuilder(db, version_id)
    
    f1 = DomainFile(id=uuid.uuid4(), repository_id=uuid.uuid4(), repository_version_id=version_id, path="app/main.py", directory_id=uuid.uuid4(), language="python")
    f2 = DomainFile(id=uuid.uuid4(), repository_id=uuid.uuid4(), repository_version_id=version_id, path="app/core/config.py", directory_id=uuid.uuid4(), language="python")
    
    i1 = DomainImport(id=uuid.uuid4(), repository_id=uuid.uuid4(), repository_version_id=version_id, file_id=f1.id, raw_statement="from app.core.config import settings")
    
    builder.build_import_edges([i1], [f1, f2])
    
    await builder.commit_to_database()
    edges = builder.edges
    
    assert len(edges) == 2
    # Check CONTAINS edge
    assert any(e.source_id == f1.id and e.target_id == i1.id and e.edge_type == SKGEdgeType.CONTAINS.value for e in edges)
    # Check IMPORTS edge
    assert any(e.source_id == f1.id and e.target_id == f2.id and e.edge_type == SKGEdgeType.IMPORTS.value for e in edges)

from app.rim.domain.models import DomainReturn

@pytest.mark.asyncio
async def test_skg_builder_returns():
    db = MockAsyncSession()
    version_id = uuid.uuid4()
    builder = SKGBuilder(db, version_id)
    
    d1 = DomainDirectory(id=uuid.uuid4(), repository_id=uuid.uuid4(), repository_version_id=version_id, path=".")
    f1 = DomainFile(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, path="app.py", directory_id=d1.id, language="python")
    
    s_user = DomainSymbol(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, file_id=f1.id, name="User", fully_qualified_name="app.py::User", symbol_type="class")
    s_func = DomainSymbol(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, file_id=f1.id, name="get_users", fully_qualified_name="app.py::get_users", symbol_type="function")
    
    ret1 = DomainReturn(id=uuid.uuid4(), repository_id=d1.repository_id, repository_version_id=version_id, file_id=f1.id, function_name="get_users", return_type="List[User]")
    
    builder.build_return_type_edges([ret1], [s_user, s_func])
    
    assert len(builder.edges) == 1
    edge = builder.edges[0]
    assert edge.source_id == s_func.id
    assert edge.target_id == s_user.id
    assert edge.edge_type == SKGEdgeType.RETURNS.value
    assert "User" in edge.provenance["evidence"]
