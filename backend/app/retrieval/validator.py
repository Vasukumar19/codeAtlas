from app.retrieval.domain.schemas import ContextPackage


class RetrievalValidator:
    def validate(self, package: ContextPackage) -> bool:
        # Check if empty context
        if not package.relevant_entities and not package.relevant_routes and not package.relevant_graph_paths:
            return False
        return True
