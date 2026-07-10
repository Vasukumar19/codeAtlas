import os

files = {
    "backend/app/retrieval/intent/__init__.py": "",
    "backend/app/retrieval/intent/detector.py": """
from app.retrieval.domain.schemas import RetrievalIntent, UserQuery

class IntentDetector:
    def detect(self, query: UserQuery) -> RetrievalIntent:
        q = query.query.lower()
        if "how" in q and ("work" in q or "flow" in q):
            return RetrievalIntent.EXECUTION_FLOW
        if "remove" in q or "break" in q or "impact" in q:
            return RetrievalIntent.IMPACT_ANALYSIS
        if "bug" in q or "fix" in q or "error" in q:
            return RetrievalIntent.BUG_INVESTIGATION
        if "route" in q or "endpoint" in q or "api" in q:
            return RetrievalIntent.ROUTE_EXPLANATION
        if "dependency" in q or "uses" in q:
            return RetrievalIntent.DEPENDENCY_ANALYSIS
        if "what does" in q and "do" in q:
            return RetrievalIntent.FUNCTION_EXPLANATION
        return RetrievalIntent.GENERAL_QUESTION
""",
    "backend/app/retrieval/planner.py": """
from app.retrieval.domain.schemas import RetrievalIntent, QueryPlan

class QueryPlanner:
    def plan(self, intent: RetrievalIntent) -> QueryPlan:
        retrievers = []
        
        if intent == RetrievalIntent.EXECUTION_FLOW:
            retrievers = ["RouteRetriever", "GraphRetriever", "FunctionRetriever"]
        elif intent == RetrievalIntent.IMPACT_ANALYSIS:
            retrievers = ["GraphRetriever", "DependencyRetriever", "MetadataRetriever"]
        elif intent == RetrievalIntent.ROUTE_EXPLANATION:
            retrievers = ["RouteRetriever", "VectorRetriever"]
        else:
            retrievers = ["VectorRetriever", "DocumentationRetriever", "MetadataRetriever"]
            
        return QueryPlan(intent=intent, retrievers=retrievers)
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
