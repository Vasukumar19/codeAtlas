import uuid
from typing import Any

from pydantic import BaseModel, Field


class AICitation(BaseModel):
    node_id: uuid.UUID
    file_path: str | None = None
    symbol_name: str | None = None
    confidence: float

class AIResponseSection(BaseModel):
    title: str
    content: str

class StructuredAIResponse(BaseModel):
    type: str
    title: str
    summary: str
    sections: list[AIResponseSection] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    citations: list[AICitation] = Field(default_factory=list)
    confidence: float
    session_id: uuid.UUID | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
