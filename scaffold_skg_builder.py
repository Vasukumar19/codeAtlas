import os

files = {
    "backend/app/skg/__init__.py": "",
    "backend/app/skg/builder.py": """
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.rim.domain.models import DomainDirectory, DomainFile, DomainSymbol, DomainImport, DomainRoute
from app.models.enums import SKGEdgeType
from app.models.skg.edge import SKGEdgeModel

class SKGBuilder:
    def __init__(self, db: AsyncSession, repository_version_id: uuid.UUID):
        self.db = db
        self.version_id = repository_version_id
        self.edges: List[SKGEdgeModel] = []

    def _add_edge(self, source_id: uuid.UUID, target_id: uuid.UUID, edge_type: SKGEdgeType, meta: dict = None):
        self.edges.append(SKGEdgeModel(
            repository_version_id=self.version_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type.value,
            metadata_=meta or {}
        ))

    def build_structural_edges(self, directories: List[DomainDirectory], files: List[DomainFile], symbols: List[DomainSymbol]):
        # Directory -> Directory
        for d in directories:
            if d.parent_id:
                self._add_edge(d.parent_id, d.id, SKGEdgeType.CONTAINS)
                
        # Directory -> File
        for f in files:
            self._add_edge(f.directory_id, f.id, SKGEdgeType.CONTAINS)
            
        # File -> Symbol (and Symbol -> Symbol)
        for s in symbols:
            if s.parent_symbol_id:
                self._add_edge(s.parent_symbol_id, s.id, SKGEdgeType.DECLARES)
            else:
                self._add_edge(s.file_id, s.id, SKGEdgeType.CONTAINS)

    def build_route_edges(self, routes: List[DomainRoute], symbols: List[DomainSymbol]):
        # Route -> Function
        for r in routes:
            self._add_edge(r.file_id, r.id, SKGEdgeType.CONTAINS)
            if r.handler:
                for s in symbols:
                    if s.name == r.handler and s.file_id == r.file_id:
                        self._add_edge(r.id, s.id, SKGEdgeType.ROUTES_TO)
                        break

    def build_import_edges(self, imports: List[DomainImport]):
        # File -> Import
        for i in imports:
            self._add_edge(i.file_id, i.id, SKGEdgeType.CONTAINS)
            # In a full implementation, we resolve i.raw_statement to a target file/module
            # and emit an IMPORTS edge. For this scope, the CONTAINS edges lay the foundation.

    async def commit_to_database(self):
        for e in self.edges:
            self.db.add(e)
        await self.db.commit()
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
