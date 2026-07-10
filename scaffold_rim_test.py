import os

files = {
    "backend/app/db/base.py": """
from app.db.base_class import Base, TimestampMixin, UUIDMixin
from app.models import Repository, RepositoryVersion, Job, ParsingReport
from app.models.rim.models import RIMDirectoryModel, RIMFileModel, RIMSymbolModel, RIMImportModel, RIMRouteModel

__all__ = ["Base", "TimestampMixin", "UUIDMixin", "Repository", "RepositoryVersion", "Job", "ParsingReport", "RIMDirectoryModel", "RIMFileModel", "RIMSymbolModel", "RIMImportModel", "RIMRouteModel"]
""",
    "backend/tests/parser/test_rim_builder.py": """
import pytest
import uuid
from app.parser.models import ParseResult
from app.rim.builder import RIMBuilderPipeline
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Mock DB Session
class MockAsyncSession:
    def __init__(self):
        self.added = []
    def add(self, obj):
        self.added.append(obj)
    async def commit(self):
        pass

@pytest.mark.asyncio
async def test_rim_builder_pipeline():
    db = MockAsyncSession()
    repo_id = uuid.uuid4()
    version_id = uuid.uuid4()
    
    pr = ParseResult(
        files=["backend/api/auth.py"],
        symbols=[{"file": "backend/api/auth.py", "name": "login", "type": "symbol.function.name"}],
        imports=[{"file": "backend/api/auth.py", "raw": "import os"}],
        routes=[{"file": "backend/api/auth.py", "method": "POST", "path": "/login", "handler": "login"}],
        language="python",
        parser_version="1.0",
        parse_duration=0.1
    )
    
    pipeline = RIMBuilderPipeline(db, repo_id, version_id)
    pipeline.build_from_parse_result(pr)
    await pipeline.commit_to_database()
    
    assert len(pipeline.directories) == 2 # "." and "backend/api"
    assert len(pipeline.files) == 1
    assert len(pipeline.symbols) == 1
    assert len(pipeline.imports) == 1
    assert len(pipeline.routes) == 1
    
    # Verify DB commits
    assert len(db.added) == 6 # 2 dirs, 1 file, 1 symbol, 1 import, 1 route
    
    file_obj = pipeline.files[0]
    sym_obj = pipeline.symbols[0]
    
    # Stable IDs check
    from app.rim.identity import IdentityGenerator
    expected_file_id = IdentityGenerator.generate_file_id(repo_id, "backend/api/auth.py")
    expected_sym_id = IdentityGenerator.generate_symbol_id(expected_file_id, "backend/api/auth.py::login")
    
    assert file_obj.id == expected_file_id
    assert sym_obj.id == expected_sym_id
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
