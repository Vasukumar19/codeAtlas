from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ParseResult(BaseModel):
    files: List[str] = Field(default_factory=list)
    ast: Any = None  # In-memory Tree-sitter object
    symbols: List[Dict[str, Any]] = Field(default_factory=list)
    imports: List[Dict[str, Any]] = Field(default_factory=list)
    routes: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    
    language: str
    parser_version: str
    parse_duration: float
    
    model_config = {"arbitrary_types_allowed": True}
