import uuid

from pydantic import BaseModel, Field


class KnowledgeProvenance(BaseModel):
    generated_by: str
    generated_at: str
    confidence: float
    evidence: str | None = None

class KnowledgeIdentity(BaseModel):
    id: uuid.UUID
    entity_type: str
    repository_id: uuid.UUID
    repository_version_id: uuid.UUID
    rim_entity_id: uuid.UUID
    skg_node_id: uuid.UUID | None = None

class KnowledgeSemantics(BaseModel):
    summary: tuple[str, float] | None = None # (Text, Confidence)
    purposes: list[tuple[str, float]] = Field(default_factory=list)
    responsibilities: list[tuple[str, float]] = Field(default_factory=list)

class KnowledgeMetrics(BaseModel):
    complexity: tuple[str, float] | None = None
    risk_level: tuple[str, float] | None = None

class KnowledgeDocumentation(BaseModel):
    docstrings: list[str] = Field(default_factory=list)
    comments: list[str] = Field(default_factory=list)

class KnowledgeRelationships(BaseModel):
    dependencies: list[tuple[str, float]] = Field(default_factory=list)

class KnowledgeMetadata(BaseModel):
    framework: tuple[str, float] | None = None
    layer: tuple[str, float] | None = None
    tags: list[tuple[str, float]] = Field(default_factory=list)

class KnowledgeNode(BaseModel):
    identity: KnowledgeIdentity
    semantics: KnowledgeSemantics = Field(default_factory=KnowledgeSemantics)
    metrics: KnowledgeMetrics = Field(default_factory=KnowledgeMetrics)
    documentation: KnowledgeDocumentation = Field(default_factory=KnowledgeDocumentation)
    relationships: KnowledgeRelationships = Field(default_factory=KnowledgeRelationships)
    metadata: KnowledgeMetadata = Field(default_factory=KnowledgeMetadata)
    provenance: dict[str, KnowledgeProvenance] = Field(default_factory=dict)
