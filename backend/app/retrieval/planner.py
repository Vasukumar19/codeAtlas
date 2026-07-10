from app.retrieval.domain.schemas import QueryPlan, RetrievalIntent


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
