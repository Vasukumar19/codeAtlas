import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SKGEdgeType
from app.models.skg.edge import SKGEdgeModel
from app.rim.domain.models import (
    DomainDirectory,
    DomainFile,
    DomainImport,
    DomainRoute,
    DomainSymbol,
    DomainCall,
)


class SKGBuilder:
    def __init__(self, db: AsyncSession, repository_version_id: uuid.UUID):
        self.db = db
        self.version_id = repository_version_id
        self.edges: list[SKGEdgeModel] = []

    def _add_edge(self, source_id: uuid.UUID, target_id: uuid.UUID, edge_type: SKGEdgeType, meta: dict = None, evidence: str = None):
        self.edges.append(SKGEdgeModel(
            repository_version_id=self.version_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type.value,
            metadata_=meta or {},
            provenance={"generated_by": "SKGBuilder", "evidence": evidence}
        ))

    def build_structural_edges(self, directories: list[DomainDirectory], files: list[DomainFile], symbols: list[DomainSymbol]):
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

    def build_route_edges(self, routes: list[DomainRoute], symbols: list[DomainSymbol]):
        # Route -> Function
        for r in routes:
            self._add_edge(r.file_id, r.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Route')
            if r.handler:
                for s in symbols:
                    if s.name == r.handler and s.file_id == r.file_id:
                        self._add_edge(r.id, s.id, SKGEdgeType.ROUTES_TO, evidence='RIM Route Handler Match')
                        break

    def build_import_edges(self, imports: list[DomainImport], files: list[DomainFile]):
        # File -> Import
        # Resolve import to target file
        file_map = {f.id: f for f in files}
        path_to_file = {f.path: f.id for f in files}
        
        for i in imports:
            self._add_edge(i.file_id, i.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Import')
            
            # Simple heuristic resolution for Python and JS
            source_file = file_map.get(i.file_id)
            if not source_file:
                continue
                
            raw = i.raw_statement
            target_path = None
            
            # Python: "from x.y import z" or "import x.y"
            if source_file.language == "python":
                parts = raw.replace("from ", "").replace("import ", "").split(" ")[0].split(".")
                target_path = "/".join(parts) + ".py"
            
            # JS/TS: import { x } from './y'
            elif source_file.language in ["javascript", "typescript", "java", "go", "c-sharp"]:
                if " from " in raw:
                    import_path = raw.split(" from ")[-1].strip(" \"';")
                else:
                    import_path = raw.split(" ")[-1].strip(" \"';")
                
                if import_path.startswith("."):
                    import_path = import_path.replace("./", "").replace("../", "")
                    # Naive append
                    target_path = import_path
                else:
                    target_path = import_path
                    
            if target_path:
                # Find matching file (naive suffix match for cross-language)
                for f_path, f_id in path_to_file.items():
                    if f_path.endswith(target_path) or f_path.endswith(f"{target_path}.js") or f_path.endswith(f"{target_path}.ts"):
                        self._add_edge(i.file_id, f_id, SKGEdgeType.IMPORTS, evidence='Heuristic Import Resolution')
                        break

    def build_call_edges(self, calls: list[DomainCall], symbols: list[DomainSymbol]):
        symbol_map = {}
        for s in symbols:
            # We index symbols by name. A robust solution would also account for receiver and scoping.
            if s.name not in symbol_map:
                symbol_map[s.name] = []
            symbol_map[s.name].append(s)
            
        for c in calls:
            # For each call, try to resolve to a symbol
            if c.function_name in symbol_map:
                for target_symbol in symbol_map[c.function_name]:
                    self._add_edge(c.file_id, target_symbol.id, SKGEdgeType.CALLS, evidence='Heuristic Call Resolution')
                    # If this call is inside a function, we'd ideally link Function -> Function. 
                    # For now, File -> Function is a baseline for CALLS heuristics.

    def build_advanced_edges(self, symbols: list[DomainSymbol]):
        # Placeholder for EXTENDS, IMPLEMENTS, RETURNS, DEPENDS_ON, REFERENCES
        # A robust implementation requires extracting parent classes, interfaces, return types
        # and variable references from the AST.
        pass

    async def commit_to_database(self):
        for e in self.edges:
            self.db.add(e)
        await self.db.commit()
