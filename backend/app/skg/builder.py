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
    DomainInheritance,
    DomainReturn,
)

import re

def _extract_inner_types(type_str: str) -> list[str]:
    # Find all capitalized or identifier-like tokens in the type string,
    # ignoring generic keywords and primitive types.
    ignore_words = {'list', 'dict', 'set', 'tuple', 'union', 'optional', 'map',
                    'List', 'Dict', 'Set', 'Tuple', 'Union', 'Optional', 'Map',
                    'str', 'int', 'float', 'bool', 'None', 'any', 'Any', 'void', 'Void'}
    tokens = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', type_str)
    return [t for t in tokens if t not in ignore_words]



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
            self._add_edge(
                r.file_id,
                r.id,
                SKGEdgeType.CONTAINS,
                meta={"byte_offset": r.byte_offset},
                evidence='RIM File Contains Route',
            )
            if r.handler:
                for s in symbols:
                    if s.name == r.handler and s.file_id == r.file_id:
                        self._add_edge(
                            r.id,
                            s.id,
                            SKGEdgeType.ROUTES_TO,
                            meta={"byte_offset": r.byte_offset},
                            evidence='RIM Route Handler Match',
                        )
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
                        meta={"confidence": 0.9, "byte_offset": c.byte_offset},
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
                        meta={"confidence": 0.8, "byte_offset": c.byte_offset},
                        evidence='Call Resolution: Imported File Match',
                    )
                continue

            # 3. Fallback to repo-wide matching
            for target_symbol in symbol_by_name[c.function_name]:
                self._add_edge(
                    source_id,
                    target_symbol.id,
                    SKGEdgeType.CALLS,
                    meta={"confidence": 0.5, "byte_offset": c.byte_offset},
                    evidence='Call Resolution: Repo-wide Fallback Match',
                )

    def build_advanced_edges(self, symbols: list[DomainSymbol]):
        pass

    def build_dependency_edges(self, files: list[DomainFile], directories: list[DomainDirectory]):
        # Roll up file imports to directory-level DEPENDS_ON edges
        file_to_dir = {f.id: f.directory_id for f in files}
        added_dependencies = set()
        
        for edge in self.edges:
            if edge.edge_type == SKGEdgeType.IMPORTS.value:
                src_dir = file_to_dir.get(edge.source_id)
                tgt_dir = file_to_dir.get(edge.target_id)
                
                if src_dir and tgt_dir and src_dir != tgt_dir:
                    dep_key = (src_dir, tgt_dir)
                    if dep_key not in added_dependencies:
                        self._add_edge(src_dir, tgt_dir, SKGEdgeType.DEPENDS_ON, evidence='Rolled up file imports')
                        added_dependencies.add(dep_key)

    def build_inheritance_edges(self, inheritance: list[DomainInheritance], symbols: list[DomainSymbol]):
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

        for inh in inheritance:
            if inh.parent_name not in symbol_by_name:
                continue

            # Find the symbol representing the subclass
            subclass_symbol = symbol_by_file_and_name.get((inh.file_id, inh.class_name))
            if not subclass_symbol:
                continue

            edge_type = SKGEdgeType.EXTENDS if inh.inheritance_type == "extends" else SKGEdgeType.IMPLEMENTS

            # 1. Try to resolve to the same file
            same_file_symbols = [s for s in symbol_by_name[inh.parent_name] if s.file_id == inh.file_id]
            if same_file_symbols:
                for target_symbol in same_file_symbols:
                    self._add_edge(
                        subclass_symbol.id,
                        target_symbol.id,
                        edge_type,
                        meta={"confidence": 0.9},
                        evidence='Inheritance Resolution: Same File Match',
                    )
                continue

            # 2. Try to resolve to imported files
            imports = imported_files.get(inh.file_id, set())
            imported_symbols = [s for s in symbol_by_name[inh.parent_name] if s.file_id in imports]
            if imported_symbols:
                for target_symbol in imported_symbols:
                    self._add_edge(
                        subclass_symbol.id,
                        target_symbol.id,
                        edge_type,
                        meta={"confidence": 0.8},
                        evidence='Inheritance Resolution: Imported File Match',
                    )
                continue

            # 3. Fallback to repo-wide matching
            for target_symbol in symbol_by_name[inh.parent_name]:
                self._add_edge(
                    subclass_symbol.id,
                    target_symbol.id,
                    edge_type,
                    meta={"confidence": 0.5},
                    evidence='Inheritance Resolution: Repo-wide Fallback Match',
                )

    def build_return_type_edges(self, returns: list[DomainReturn], symbols: list[DomainSymbol]):
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

        for ret in returns:
            # Find the symbol representing the function
            func_symbol = symbol_by_file_and_name.get((ret.file_id, ret.function_name))
            if not func_symbol:
                continue

            # Extract all potential inner type names (e.g. List[User] -> ['User'])
            inner_types = _extract_inner_types(ret.return_type)
            if not inner_types:
                inner_types = [ret.return_type]

            for type_name in inner_types:
                if type_name not in symbol_by_name:
                    continue

                # 1. Try to resolve to the same file
                same_file_symbols = [s for s in symbol_by_name[type_name] if s.file_id == ret.file_id]
                if same_file_symbols:
                    for target_symbol in same_file_symbols:
                        self._add_edge(
                            func_symbol.id,
                            target_symbol.id,
                            SKGEdgeType.RETURNS,
                            meta={"confidence": 0.9},
                            evidence=f'Return Type Resolution ({type_name}): Same File Match',
                        )
                    continue

                # 2. Try to resolve to imported files
                imports = imported_files.get(ret.file_id, set())
                imported_symbols = [s for s in symbol_by_name[type_name] if s.file_id in imports]
                if imported_symbols:
                    for target_symbol in imported_symbols:
                        self._add_edge(
                            func_symbol.id,
                            target_symbol.id,
                            SKGEdgeType.RETURNS,
                            meta={"confidence": 0.8},
                            evidence=f'Return Type Resolution ({type_name}): Imported File Match',
                        )
                    continue

                # 3. Fallback to repo-wide matching
                for target_symbol in symbol_by_name[type_name]:
                    self._add_edge(
                        func_symbol.id,
                        target_symbol.id,
                        SKGEdgeType.RETURNS,
                        meta={"confidence": 0.5},
                        evidence=f'Return Type Resolution ({type_name}): Repo-wide Fallback Match',
                    )

    async def commit_to_database(self):
        for e in self.edges:
            self.db.add(e)
        await self.db.commit()
