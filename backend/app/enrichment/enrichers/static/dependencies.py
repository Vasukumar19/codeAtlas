from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.models.enums import SKGEdgeType


class DependencyEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        if context.node.identity.entity_type == "File":
            deps = []
            for edge in context.skg_edges:
                if getattr(edge, 'edge_type', None) == SKGEdgeType.IMPORTS.value:
                    # In a real app we would join with RIMImportModel to get the raw statement
                    # Or look at target file path. Here we just note it has a dependency.
                    deps.append(("Has external dependency", 0.8))
            if deps:
                context.node.relationships.dependencies.extend(deps)
                context.add_provenance('dependencies', 'DependencyEnricher', 0.8, 'Derived from SKG import edges')
        return context
