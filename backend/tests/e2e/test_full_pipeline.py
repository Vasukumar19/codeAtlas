import pytest
import uuid
import os
from pathlib import Path

from app.parser.plugins.python_plugin import PythonPlugin
from app.rim.builder import RIMBuilderPipeline
from app.skg.builder import SKGBuilder
from app.enrichment.pipeline import KnowledgePipeline
from app.models.enums import SKGEdgeType
from app.rim.domain.models import DomainRoute

class MockAsyncSession:
    def __init__(self):
        self.added = []
    def add(self, obj):
        self.added.append(obj)
    async def commit(self):
        pass

@pytest.mark.asyncio
async def test_full_e2e_pipeline():
    repo_id = uuid.uuid4()
    version_id = uuid.uuid4()
    db = MockAsyncSession()
    
    # 1. PARSER
    fixtures_dir = Path(__file__).parent.parent.parent / "tests" / "fixtures" / "python" / "fastapi_demo"
    # Use relative paths for the mock
    filepaths = [
        str(fixtures_dir / "app.py"),
        str(fixtures_dir / "auth.py"),
        str(fixtures_dir / "users.py")
    ]
    # For RIM Builder to work correctly, files in ParseResult should be relative to repo root
    rel_filepaths = ["app.py", "auth.py", "users.py"]
    
    parse_result = PythonPlugin.parse_files(filepaths)
    # Patch the parse_result files to be relative
    parse_result.files = rel_filepaths
    
    # Also patch symbols/imports/routes
    for s in parse_result.symbols:
        s["file"] = os.path.basename(s["file"])
    for i in parse_result.imports:
        i["file"] = os.path.basename(i["file"])
    for r in parse_result.routes:
        r["file"] = os.path.basename(r["file"])
    
    # 2. RIM BUILDER
    rim_builder = RIMBuilderPipeline(db, repo_id, version_id)
    rim_builder.build_from_parse_result(parse_result)
    
    # 3. SKG BUILDER
    skg_builder = SKGBuilder(db, version_id)
    skg_builder.build_structural_edges(list(rim_builder.directories.values()), rim_builder.files, rim_builder.symbols)
    skg_builder.build_route_edges(rim_builder.routes, rim_builder.symbols)
    skg_builder.build_import_edges(rim_builder.imports, rim_builder.files)
    
    assert len(skg_builder.edges) > 0
    
    # 4. KNOWLEDGE PIPELINE
    knowledge_pipeline = KnowledgePipeline()
    
    auth_route_node = None
    
    # Process Routes
    for route in rim_builder.routes:
        if "/login" in route.path:
            auth_route_node = await knowledge_pipeline.execute(
                rim_entity=route,
                entity_type="Route",
                skg_edges=[e for e in skg_builder.edges if e.source_id == route.id or e.target_id == route.id]
            )
            
    assert auth_route_node is not None
    
    # Verify Semantics
    assert any(p[0] == "Authentication" for p in auth_route_node.semantics.purposes)
    
    # Verify Provenance
    assert "purposes" in auth_route_node.provenance
    assert auth_route_node.provenance["purposes"].generated_by == "PurposeEnricher"
    assert auth_route_node.provenance["purposes"].evidence == "Name/Path heuristics match"
    
    # Verify SKG Edge Provenance
    route_edges = [e for e in skg_builder.edges if e.source_id == auth_route_node.identity.rim_entity_id]
    routes_to_edge = next((e for e in route_edges if e.edge_type == SKGEdgeType.ROUTES_TO.value), None)
    
    assert routes_to_edge is not None
    assert routes_to_edge.provenance["generated_by"] == "SKGBuilder"
    assert routes_to_edge.provenance["evidence"] == "RIM Route Handler Match"
