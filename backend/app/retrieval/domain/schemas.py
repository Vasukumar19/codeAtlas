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
