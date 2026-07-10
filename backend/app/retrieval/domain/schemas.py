import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


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
    session_context: dict[str, Any] | None = None

class QueryPlan(BaseModel):
    intent: RetrievalIntent
    retrievers: list[str] = Field(default_factory=list)

class RetrievalResult(BaseModel):
    node_id: uuid.UUID
    entity_type: str
    relevance_score: float
    evidence: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    
class ContextPackage(BaseModel):
    repository_summary: str | None = None
    relevant_entities: list[RetrievalResult] = Field(default_factory=list)
    relevant_graph_paths: list[str] = Field(default_factory=list)
    relevant_routes: list[RetrievalResult] = Field(default_factory=list)
    relevant_documentation: list[RetrievalResult] = Field(default_factory=list)
    confidence_scores: dict[str, float] = Field(default_factory=dict)
