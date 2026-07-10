import os

files = {
    "backend/app/enrichment/domain/__init__.py": "",
    "backend/app/enrichment/domain/schemas.py": """
from typing import List, Optional, Tuple, Any
from pydantic import BaseModel, Field
import uuid

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
""",
    "backend/app/models/enrichment/__init__.py": "",
    "backend/app/models/enrichment/node.py": """
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import JSON, String
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class KnowledgeNodeModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "knowledge_nodes"
    
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    repository_version_id: Mapped[uuid.UUID] = mapped_column(index=True)
    rim_entity_id: Mapped[uuid.UUID] = mapped_column(index=True)
    skg_node_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    entity_type: Mapped[str] = mapped_column(String, index=True)
    
    semantics: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    documentation: Mapped[dict] = mapped_column(JSON, default=dict)
    relationships: Mapped[dict] = mapped_column(JSON, default=dict)
    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# Update base.py
base_path = "c:/Users/kumar/project/codeAtlas/backend/app/db/base.py"
with open(base_path, "r", encoding="utf-8") as f:
    base_content = f.read()

if "KnowledgeNodeModel" not in base_content:
    base_content = base_content.replace(
        "from app.models.skg.edge import SKGEdgeModel",
        "from app.models.enrichment.node import KnowledgeNodeModel\nfrom app.models.skg.edge import SKGEdgeModel"
    )
    base_content = base_content.replace(
        '"SKGEdgeModel"',
        '"SKGEdgeModel", "KnowledgeNodeModel"'
    )
    with open(base_path, "w", encoding="utf-8") as f:
        f.write(base_content)
