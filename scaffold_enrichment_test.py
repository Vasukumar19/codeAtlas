import os

files = {
    "backend/tests/enrichment/__init__.py": "",
    "backend/tests/enrichment/test_pipeline.py": """
import pytest
import uuid
from app.enrichment.pipeline import KnowledgePipeline
from app.rim.domain.models import DomainRoute, DomainSymbol

@pytest.mark.asyncio
async def test_knowledge_pipeline():
    pipeline = KnowledgePipeline()
    
    # 1. Test Route Enrichment
    route_id = uuid.uuid4()
    repo_id = uuid.uuid4()
    version_id = uuid.uuid4()
    
    route = DomainRoute(
        id=route_id, repository_id=repo_id, repository_version_id=version_id,
        file_id=uuid.uuid4(), method="POST", path="/api/v1/auth/login", handler="login"
    )
    
    # Execute Pipeline
    node = await pipeline.execute(route, "Route", [])
    
    # Assert Identity
    assert node.identity.entity_type == "Route"
    assert node.identity.rim_entity_id == route_id
    
    # Assert Semantics
    # Purpose should be Authentication
    assert any(p[0] == "Authentication" for p in node.semantics.purposes)
    
    # Summary should be generated based on purpose
    assert node.semantics.summary is not None
    assert "Endpoint for authentication" in node.semantics.summary[0]
    
    # Assert Metrics (Low risk since 0 todos)
    assert node.metrics.risk_level[0] == "Low"

    # 2. Test Symbol Layer Enrichment
    symbol = DomainSymbol(
        id=uuid.uuid4(), repository_id=repo_id, repository_version_id=version_id,
        file_id=uuid.uuid4(), name="AuthController", fully_qualified_name="auth.py::AuthController", symbol_type="class"
    )
    node_sym = await pipeline.execute(symbol, "Class", [])
    assert node_sym.metadata.layer[0] == "Controller"
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
