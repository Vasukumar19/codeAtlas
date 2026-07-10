import os

files = {
    "backend/app/rim/domain/__init__.py": "",
    "backend/app/rim/domain/models.py": """
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class DomainEntity:
    id: uuid.UUID
    repository_id: uuid.UUID
    repository_version_id: uuid.UUID
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DomainDirectory(DomainEntity):
    path: str
    parent_id: Optional[uuid.UUID] = None
    child_directories: List[uuid.UUID] = field(default_factory=list)
    files: List[uuid.UUID] = field(default_factory=list)

@dataclass
class DomainFile(DomainEntity):
    path: str
    directory_id: uuid.UUID
    language: str

@dataclass
class DomainSymbol(DomainEntity):
    name: str
    fully_qualified_name: str
    file_id: uuid.UUID
    symbol_type: str
    parent_symbol_id: Optional[uuid.UUID] = None
    imports_used: List[uuid.UUID] = field(default_factory=list)
    routes_exposed: List[uuid.UUID] = field(default_factory=list)

@dataclass
class DomainImport(DomainEntity):
    file_id: uuid.UUID
    raw_statement: str

@dataclass
class DomainRoute(DomainEntity):
    file_id: uuid.UUID
    method: str
    path: str
    handler: str
""",
    "backend/app/rim/identity.py": """
import uuid

NAMESPACE_RIM = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')

class IdentityGenerator:
    @staticmethod
    def generate_repository_id(owner: str, name: str) -> uuid.UUID:
        sig = f"repository:{owner}/{name}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_directory_id(repo_id: uuid.UUID, path: str) -> uuid.UUID:
        sig = f"directory:{repo_id}:{path}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_file_id(repo_id: uuid.UUID, path: str) -> uuid.UUID:
        sig = f"file:{repo_id}:{path}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_symbol_id(file_id: uuid.UUID, fully_qualified_name: str) -> uuid.UUID:
        sig = f"symbol:{file_id}:{fully_qualified_name}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_import_id(file_id: uuid.UUID, raw: str) -> uuid.UUID:
        sig = f"import:{file_id}:{raw}"
        return uuid.uuid5(NAMESPACE_RIM, sig)

    @staticmethod
    def generate_route_id(file_id: uuid.UUID, method: str, path: str) -> uuid.UUID:
        sig = f"route:{file_id}:{method}:{path}"
        return uuid.uuid5(NAMESPACE_RIM, sig)
""",
    "backend/app/models/rim/__init__.py": "",
    "backend/app/models/rim/models.py": """
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, JSON, String
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class RIMDirectoryModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_directories"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(String, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rim_directories.id"))

class RIMFileModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_files"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    directory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_directories.id"))
    path: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)

class RIMSymbolModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_symbols"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_files.id"))
    name: Mapped[str] = mapped_column(String)
    fully_qualified_name: Mapped[str] = mapped_column(String)
    symbol_type: Mapped[str] = mapped_column(String)
    parent_symbol_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("rim_symbols.id"))

class RIMImportModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_imports"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_files.id"))
    raw_statement: Mapped[str] = mapped_column(String)

class RIMRouteModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "rim_routes"
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rim_files.id"))
    method: Mapped[str] = mapped_column(String)
    path: Mapped[str] = mapped_column(String)
    handler: Mapped[str] = mapped_column(String)
""",
    "backend/app/rim/builder.py": """
import uuid
import os
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.parser.models import ParseResult
from app.rim.domain.models import DomainDirectory, DomainFile, DomainSymbol, DomainImport, DomainRoute
from app.rim.identity import IdentityGenerator
from app.models.rim.models import RIMDirectoryModel, RIMFileModel, RIMSymbolModel, RIMImportModel, RIMRouteModel

class RIMBuilderPipeline:
    def __init__(self, db: AsyncSession, repository_id: uuid.UUID, repository_version_id: uuid.UUID):
        self.db = db
        self.repo_id = repository_id
        self.version_id = repository_version_id
        
        self.directories: Dict[str, DomainDirectory] = {}
        self.files: List[DomainFile] = []
        self.symbols: List[DomainSymbol] = []
        self.imports: List[DomainImport] = []
        self.routes: List[DomainRoute] = []

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
            
        await self.db.commit()
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
