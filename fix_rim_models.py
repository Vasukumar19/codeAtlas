import os

files = {
    "backend/app/rim/domain/models.py": """
import uuid
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass(kw_only=True)
class DomainEntity:
    id: uuid.UUID
    repository_id: uuid.UUID
    repository_version_id: uuid.UUID
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(kw_only=True)
class DomainDirectory(DomainEntity):
    path: str
    parent_id: Optional[uuid.UUID] = None
    child_directories: List[uuid.UUID] = field(default_factory=list)
    files: List[uuid.UUID] = field(default_factory=list)

@dataclass(kw_only=True)
class DomainFile(DomainEntity):
    path: str
    directory_id: uuid.UUID
    language: str

@dataclass(kw_only=True)
class DomainSymbol(DomainEntity):
    name: str
    fully_qualified_name: str
    file_id: uuid.UUID
    symbol_type: str
    parent_symbol_id: Optional[uuid.UUID] = None
    imports_used: List[uuid.UUID] = field(default_factory=list)
    routes_exposed: List[uuid.UUID] = field(default_factory=list)

@dataclass(kw_only=True)
class DomainImport(DomainEntity):
    file_id: uuid.UUID
    raw_statement: str

@dataclass(kw_only=True)
class DomainRoute(DomainEntity):
    file_id: uuid.UUID
    method: str
    path: str
    handler: str
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
