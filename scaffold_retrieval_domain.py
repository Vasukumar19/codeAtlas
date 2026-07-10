import os

files = {
    "backend/app/retrieval/__init__.py": "",
    "backend/app/retrieval/domain/__init__.py": "",
    "backend/app/retrieval/domain/schemas.py": """
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class RetrievalIntent(str, Enum):
    ARCHITECTURE = "Architecture"
    EXECUTION_FLOW = "Execution Flow"
    REPOSITORY_OVERVIEW = "Repository Overview"
    FUNCTION_EXPLANATION = "Function Explanation"
    CLASS_EXPLANATION = "Class Explanation"
    ROUTE_EXPLANATION = "Route Explanation"
    DEPENDENCY_ANALYSIS = "Dependency Analysis"
    IMPACT_ANALYSIS = "Impact Analysis"
    BUG_INVESTIGATION = "Bug Investigation"
    DOCUMENTATION = "Documentation"
    SEARCH = "Search"
    GENERAL_QUESTION = "General Question"

class UserQuery(BaseModel):
    query: str
    repository_id: uuid.UUID
    repository_version_id: uuid.UUID
    session_context: Optional[Dict[str, Any]] = None

class QueryPlan(BaseModel):
    intent: RetrievalIntent
    retrievers: List[str] = Field(default_factory=list)

class RetrievalResult(BaseModel):
    node_id: uuid.UUID
    entity_type: str
    relevance_score: float
    evidence: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
class ContextPackage(BaseModel):
    repository_summary: Optional[str] = None
    relevant_entities: List[RetrievalResult] = Field(default_factory=list)
    relevant_graph_paths: List[str] = Field(default_factory=list)
    relevant_routes: List[RetrievalResult] = Field(default_factory=list)
    relevant_documentation: List[RetrievalResult] = Field(default_factory=list)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
""",
    "backend/app/models/retrieval/__init__.py": "",
    "backend/app/models/retrieval/trace.py": """
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, JSON
from app.db.base_class import Base, UUIDMixin, TimestampMixin

class RetrievalTraceModel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "retrieval_traces"
    
    repository_id: Mapped[uuid.UUID] = mapped_column(index=True)
    user_query: Mapped[str] = mapped_column(String)
    intent: Mapped[str] = mapped_column(String)
    plan: Mapped[dict] = mapped_column(JSON)
    execution_time_ms: Mapped[int] = mapped_column(Integer)
    final_context_hash: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
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

if "RetrievalTraceModel" not in base_content:
    base_content = base_content.replace(
        "from app.models.embeddings.metadata import EmbeddingMetadataModel",
        "from app.models.embeddings.metadata import EmbeddingMetadataModel\nfrom app.models.retrieval.trace import RetrievalTraceModel"
    )
    base_content = base_content.replace(
        '"EmbeddingMetadataModel"',
        '"EmbeddingMetadataModel", "RetrievalTraceModel"'
    )
    with open(base_path, "w", encoding="utf-8") as f:
        f.write(base_content)
