from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid

class AICitation(BaseModel):
    node_id: uuid.UUID
    file_path: Optional[str] = None
    symbol_name: Optional[str] = None
    confidence: float

class AIResponseSection(BaseModel):
    title: str
    content: str

class StructuredAIResponse(BaseModel):
    type: str
    title: str
    summary: str
    sections: List[AIResponseSection] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    citations: List[AICitation] = Field(default_factory=list)
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
