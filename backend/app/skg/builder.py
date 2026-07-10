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

    def _add_edge(self, source_id: uuid.UUID, target_id: uuid.UUID, edge_type: SKGEdgeType, meta: dict = None, evidence: str = None):
        self.edges.append(SKGEdgeModel(
            repository_version_id=self.version_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type.value,
            metadata_=meta or {},
            provenance={"generated_by": "SKGBuilder", "evidence": evidence}
        ))

    def build_structural_edges(self, directories: List[DomainDirectory], files: List[DomainFile], symbols: List[DomainSymbol]):
        # Directory -> Directory
        for d in directories:
            if d.parent_id:
                self._add_edge(d.parent_id, d.id, SKGEdgeType.CONTAINS, evidence='RIM Directory Hierarchy')
                
        # Directory -> File
        for f in files:
            self._add_edge(f.directory_id, f.id, SKGEdgeType.CONTAINS, evidence='RIM Directory Contains File')
            
        # File -> Symbol (and Symbol -> Symbol)
        for s in symbols:
            if s.parent_symbol_id:
                self._add_edge(s.parent_symbol_id, s.id, SKGEdgeType.DECLARES, evidence='RIM Symbol Declares Child')
            else:
                self._add_edge(s.file_id, s.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Symbol')

    def build_route_edges(self, routes: List[DomainRoute], symbols: List[DomainSymbol]):
        # Route -> Function
        for r in routes:
            self._add_edge(r.file_id, r.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Route')
            if r.handler:
                for s in symbols:
                    if s.name == r.handler and s.file_id == r.file_id:
                        self._add_edge(r.id, s.id, SKGEdgeType.ROUTES_TO, evidence='RIM Route Handler Match')
                        break

    def build_import_edges(self, imports: List[DomainImport]):
        # File -> Import
        for i in imports:
            self._add_edge(i.file_id, i.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Import')
            # In a full implementation, we resolve i.raw_statement to a target file/module
            # and emit an IMPORTS edge. For this scope, the CONTAINS edges lay the foundation.

    async def commit_to_database(self):
        for e in self.edges:
            self.db.add(e)
        await self.db.commit()
