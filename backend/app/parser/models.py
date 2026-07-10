from typing import Any

from pydantic import BaseModel, Field


class ParseResult(BaseModel):
    files: list[str] = Field(default_factory=list)
    ast: Any = None  # In-memory Tree-sitter object
    symbols: list[dict[str, Any]] = Field(default_factory=list)
    imports: list[dict[str, Any]] = Field(default_factory=list)
    routes: list[dict[str, Any]] = Field(default_factory=list)
    calls: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    errors: list[dict[str, Any]] = Field(default_factory=list)
    statistics: dict[str, Any] = Field(default_factory=dict)
    
    language: str
    parser_version: str
    parse_duration: float
    
    model_config = {"arbitrary_types_allowed": True}
