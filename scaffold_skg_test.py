import os

files = {
    "backend/tests/skg/__init__.py": "",
    "backend/tests/skg/test_skg_builder.py": """
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
    assert len(edges) == 3
    
    # Check File CONTAINS Symbol
    assert any(e.source_id == f1.id and e.target_id == s1.id and e.edge_type == SKGEdgeType.CONTAINS.value for e in edges)
    # Check Route ROUTES_TO Symbol
    assert any(e.source_id == r1.id and e.target_id == s1.id and e.edge_type == SKGEdgeType.ROUTES_TO.value for e in edges)
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
