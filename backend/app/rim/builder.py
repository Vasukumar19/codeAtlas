import os
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rim.models import (
    RIMDirectoryModel,
    RIMFileModel,
    RIMImportModel,
    RIMRouteModel,
    RIMSymbolModel,
    RIMCallModel,
)
from app.parser.models import ParseResult
from app.rim.domain.models import (
    DomainDirectory,
    DomainFile,
    DomainImport,
    DomainRoute,
    DomainSymbol,
    DomainCall,
)
from app.rim.identity import IdentityGenerator


class RIMBuilderPipeline:
    def __init__(self, db: AsyncSession, repository_id: uuid.UUID, repository_version_id: uuid.UUID):
        self.db = db
        self.repo_id = repository_id
        self.version_id = repository_version_id
        
        self.directories: dict[str, DomainDirectory] = {}
        self.files: list[DomainFile] = []
        self.symbols: list[DomainSymbol] = []
        self.imports: list[DomainImport] = []
        self.routes: list[DomainRoute] = []
        self.calls: list[DomainCall] = []

    def _ensure_directory(self, path: str) -> uuid.UUID:
        dir_path = os.path.dirname(path)
        if not dir_path:
            dir_path = "."
            
        if dir_path in self.directories:
            return self.directories[dir_path].id
            
        dir_id = IdentityGenerator.generate_directory_id(self.repo_id, dir_path)
        parent_id = None
        
        if dir_path != ".":
            parent_id = self._ensure_directory(dir_path)
            
        domain_dir = DomainDirectory(
            id=dir_id, repository_id=self.repo_id, repository_version_id=self.version_id,
            path=dir_path, parent_id=parent_id
        )
        self.directories[dir_path] = domain_dir
        return dir_id

    def build_from_parse_result(self, pr: ParseResult):
        # 1. Validation (Schema validated by Pydantic ParseResult)
        
        # 2 & 3. Normalization & Identity Assignment
        for filepath in pr.files:
            dir_id = self._ensure_directory(filepath)
            file_id = IdentityGenerator.generate_file_id(self.repo_id, filepath)
            
            self.files.append(DomainFile(
                id=file_id, repository_id=self.repo_id, repository_version_id=self.version_id,
                path=filepath, directory_id=dir_id, language=pr.language
            ))

        for sym in pr.symbols:
            filepath = sym["file"]
            file_id = IdentityGenerator.generate_file_id(self.repo_id, filepath)
            fqn = f"{filepath}::{sym['name']}"
            sym_id = IdentityGenerator.generate_symbol_id(file_id, fqn)
            
            self.symbols.append(DomainSymbol(
                id=sym_id, repository_id=self.repo_id, repository_version_id=self.version_id,
                name=sym["name"], fully_qualified_name=fqn, file_id=file_id, symbol_type=sym["type"]
            ))
            
        for imp in pr.imports:
            filepath = imp["file"]
            file_id = IdentityGenerator.generate_file_id(self.repo_id, filepath)
            imp_id = IdentityGenerator.generate_import_id(file_id, imp["raw"])
            self.imports.append(DomainImport(
                id=imp_id, repository_id=self.repo_id, repository_version_id=self.version_id,
                file_id=file_id, raw_statement=imp["raw"]
            ))
            
        for route in pr.routes:
            filepath = route["file"]
            file_id = IdentityGenerator.generate_file_id(self.repo_id, filepath)
            route_id = IdentityGenerator.generate_route_id(file_id, route["method"], route["path"])
            self.routes.append(DomainRoute(
                id=route_id, repository_id=self.repo_id, repository_version_id=self.version_id,
                file_id=file_id, method=route["method"], path=route["path"], handler=route.get("handler", "")
            ))
            
        for call in getattr(pr, "calls", []):
            filepath = call["file"]
            file_id = IdentityGenerator.generate_file_id(self.repo_id, filepath)
            call_id = uuid.uuid4() # We can use a random UUID since calls are transient edges often
            self.calls.append(DomainCall(
                id=call_id, repository_id=self.repo_id, repository_version_id=self.version_id,
                file_id=file_id, function_name=call["function"], receiver=call.get("receiver"),
                caller_function_name=call.get("caller_function_name"), byte_offset=call.get("byte_offset")
            ))
            
        # 4. Relationship Resolution
        # Explicit hierarchical resolution would link Function->Parent Class etc. 
        # For this scope, the flat IDs and foreign keys serve as the exact basis for graphs.

    async def commit_to_database(self):
        # 5 & 6. Persistence Mapping & Database Commit
        for d in self.directories.values():
            self.db.add(RIMDirectoryModel(id=d.id, repository_id=d.repository_id, repository_version_id=d.repository_version_id, path=d.path, parent_id=d.parent_id))
            
        for f in self.files:
            self.db.add(RIMFileModel(id=f.id, repository_id=f.repository_id, repository_version_id=f.repository_version_id, directory_id=f.directory_id, path=f.path, language=f.language))
            
        for s in self.symbols:
            self.db.add(RIMSymbolModel(id=s.id, repository_id=s.repository_id, repository_version_id=s.repository_version_id, file_id=s.file_id, name=s.name, fully_qualified_name=s.fully_qualified_name, symbol_type=s.symbol_type, parent_symbol_id=s.parent_symbol_id))
            
        for i in self.imports:
            self.db.add(RIMImportModel(id=i.id, repository_id=i.repository_id, repository_version_id=i.repository_version_id, file_id=i.file_id, raw_statement=i.raw_statement))
            
        for r in self.routes:
            self.db.add(RIMRouteModel(id=r.id, repository_id=r.repository_id, repository_version_id=r.repository_version_id, file_id=r.file_id, method=r.method, path=r.path, handler=r.handler))
            
        for c in self.calls:
            self.db.add(RIMCallModel(
                id=c.id, repository_id=c.repository_id, repository_version_id=c.repository_version_id, 
                file_id=c.file_id, function_name=c.function_name, receiver=c.receiver,
                caller_function_name=c.caller_function_name, byte_offset=c.byte_offset
            ))
            
        await self.db.commit()
