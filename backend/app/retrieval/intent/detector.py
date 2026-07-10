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
