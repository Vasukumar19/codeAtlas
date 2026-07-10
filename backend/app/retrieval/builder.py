
from app.retrieval.domain.schemas import ContextPackage, RetrievalResult


class ContextBuilder:
    def build(self, ranked_results: list[RetrievalResult], repository_id: str) -> ContextPackage:
        package = ContextPackage(repository_summary="Automated repo summary")
        
        for r in ranked_results:
            if r.entity_type == "Route":
                package.relevant_routes.append(r)
            elif r.entity_type == "GraphPath":
                package.relevant_graph_paths.append(str(r.node_id))
            else:
                package.relevant_entities.append(r)
                
            package.confidence_scores[str(r.node_id)] = r.relevance_score
            
        return package
