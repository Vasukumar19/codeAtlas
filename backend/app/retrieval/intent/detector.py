import json

from app.intelligence.models.registry import ModelRegistry
from app.retrieval.domain.schemas import RetrievalIntent, UserQuery


class IntentDetector:
    async def detect(self, query: UserQuery) -> RetrievalIntent:
        provider = ModelRegistry.get("Gemini")
        if not provider:
            return self._heuristic_fallback(query)
            
        sys_inst = (
            "You are an intent router for a codebase AI. "
            "Given a user query, output ONLY a JSON object with a single key 'intent' mapping to one of: "
            "EXECUTION_FLOW, IMPACT_ANALYSIS, BUG_INVESTIGATION, ROUTE_EXPLANATION, DEPENDENCY_ANALYSIS, FUNCTION_EXPLANATION, GENERAL_QUESTION."
        )
        
        try:
            res = await provider.generate(query.query, sys_inst)
            # Try to parse json
            data = json.loads(res.strip('` \n').removeprefix('json'))
            intent_str = data.get("intent", "GENERAL_QUESTION")
            return RetrievalIntent[intent_str]
        except Exception:
            return self._heuristic_fallback(query)

    def _heuristic_fallback(self, query: UserQuery) -> RetrievalIntent:
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
