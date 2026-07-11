import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(kw_only=True)
class DomainEntity:
    id: uuid.UUID
    repository_id: uuid.UUID
    repository_version_id: uuid.UUID
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(kw_only=True)
class DomainDirectory(DomainEntity):
    path: str
    parent_id: uuid.UUID | None = None
    child_directories: list[uuid.UUID] = field(default_factory=list)
    files: list[uuid.UUID] = field(default_factory=list)

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
    parent_symbol_id: uuid.UUID | None = None
    imports_used: list[uuid.UUID] = field(default_factory=list)
    routes_exposed: list[uuid.UUID] = field(default_factory=list)

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
    byte_offset: int | None = None

@dataclass(kw_only=True)
class DomainCall(DomainEntity):
    file_id: uuid.UUID
    function_name: str
    receiver: str | None = None
    caller_function_name: str | None = None
    byte_offset: int | None = None

@dataclass(kw_only=True)
class DomainInheritance(DomainEntity):
    file_id: uuid.UUID
    class_name: str
    parent_name: str
    inheritance_type: str

@dataclass(kw_only=True)
class DomainReturn(DomainEntity):
    file_id: uuid.UUID
    function_name: str
    return_type: str
