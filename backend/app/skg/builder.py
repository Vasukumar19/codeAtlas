import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SKGEdgeType
from app.models.skg.edge import SKGEdgeModel
from app.rim.domain.models import (
    DomainCall,
    DomainDirectory,
    DomainFile,
    DomainImport,
    DomainRoute,
    DomainSymbol,
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
        symbol_by_file_and_name = {}
        symbol_by_name = {}
        for s in symbols:
            symbol_by_file_and_name[(s.file_id, s.name)] = s
            if s.name not in symbol_by_name:
                symbol_by_name[s.name] = []
            symbol_by_name[s.name].append(s)

        # Get imported files for each file from self.edges (which has IMPORTS edges)
        imported_files = {}
        for edge in self.edges:
            if edge.edge_type == SKGEdgeType.IMPORTS.value:
                if edge.source_id not in imported_files:
                    imported_files[edge.source_id] = set()
                imported_files[edge.source_id].add(edge.target_id)
            
        for c in calls:
            if c.function_name not in symbol_by_name:
                continue

            source_id = c.file_id
            if c.caller_function_name:
                caller_symbol = symbol_by_file_and_name.get((c.file_id, c.caller_function_name))
                if caller_symbol:
                    source_id = caller_symbol.id

            # 1. Try to resolve to the same file
            same_file_symbols = [s for s in symbol_by_name[c.function_name] if s.file_id == c.file_id]
            if same_file_symbols:
                for target_symbol in same_file_symbols:
                    self._add_edge(
                        source_id,
                        target_symbol.id,
                        SKGEdgeType.CALLS,
                        meta={"confidence": 0.9},
                        evidence='Call Resolution: Same File Match',
                    )
                continue

            # 2. Try to resolve to imported files
            imports = imported_files.get(c.file_id, set())
            imported_symbols = [s for s in symbol_by_name[c.function_name] if s.file_id in imports]
            if imported_symbols:
                for target_symbol in imported_symbols:
                    self._add_edge(
                        source_id,
                        target_symbol.id,
                        SKGEdgeType.CALLS,
                        meta={"confidence": 0.8},
                        evidence='Call Resolution: Imported File Match',
                    )
                continue

            # 3. Fallback to repo-wide matching
            for target_symbol in symbol_by_name[c.function_name]:
                self._add_edge(
                    source_id,
                    target_symbol.id,
                    SKGEdgeType.CALLS,
                    meta={"confidence": 0.5},
                    evidence='Call Resolution: Repo-wide Fallback Match',
                )

    def build_advanced_edges(self, symbols: list[DomainSymbol]):
        # Placeholder for EXTENDS, IMPLEMENTS, RETURNS, DEPENDS_ON, REFERENCES
        # A robust implementation requires extracting parent classes, interfaces, return types
        # and variable references from the AST.
        pass

    async def commit_to_database(self):
        for e in self.edges:
            self.db.add(e)
        await self.db.commit()
