from typing import List, Optional, Tuple, Any
from pydantic import BaseModel, Field
import uuid

from typing import Dict
from datetime import datetime

class KnowledgeProvenance(BaseModel):
    generated_by: str
    generated_at: str
    confidence: float
    evidence: Optional[str] = None

class KnowledgeIdentity(BaseModel):
    id: uuid.UUID
    entity_type: str
    repository_id: uuid.UUID
    repository_version_id: uuid.UUID
    rim_entity_id: uuid.UUID
    skg_node_id: Optional[uuid.UUID] = None

class KnowledgeSemantics(BaseModel):
    summary: Optional[Tuple[str, float]] = None # (Text, Confidence)
    purposes: List[Tuple[str, float]] = Field(default_factory=list)
    responsibilities: List[Tuple[str, float]] = Field(default_factory=list)

class KnowledgeMetrics(BaseModel):
    complexity: Optional[Tuple[str, float]] = None
    risk_level: Optional[Tuple[str, float]] = None

class KnowledgeDocumentation(BaseModel):
    docstrings: List[str] = Field(default_factory=list)
    comments: List[str] = Field(default_factory=list)

class KnowledgeRelationships(BaseModel):
    dependencies: List[Tuple[str, float]] = Field(default_factory=list)

class KnowledgeMetadata(BaseModel):
    framework: Optional[Tuple[str, float]] = None
    layer: Optional[Tuple[str, float]] = None
    tags: List[Tuple[str, float]] = Field(default_factory=list)

class KnowledgeNode(BaseModel):
    identity: KnowledgeIdentity
    semantics: KnowledgeSemantics = Field(default_factory=KnowledgeSemantics)
    metrics: KnowledgeMetrics = Field(default_factory=KnowledgeMetrics)
    documentation: KnowledgeDocumentation = Field(default_factory=KnowledgeDocumentation)
    relationships: KnowledgeRelationships = Field(default_factory=KnowledgeRelationships)
    metadata: KnowledgeMetadata = Field(default_factory=KnowledgeMetadata)
    provenance: Dict[str, KnowledgeProvenance] = Field(default_factory=dict)
