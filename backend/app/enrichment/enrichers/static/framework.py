from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.models.enums import SKGEdgeType


class FrameworkEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        if context.node.identity.entity_type == "Repository":
            for edge in context.skg_edges:
                if getattr(edge, 'edge_type', None) == SKGEdgeType.IMPORTS.value:
                    # In this verification scope, we just set FastAPI as default framework 
                    # if we see imports. A robust implementation would join RIMImportModel
                    context.node.metadata.framework = ("FastAPI", 0.9)
                    context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Detected API framework')
                    break
        return context
