from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.rim.domain.models import DomainImport

class DependencyEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        if context.node.identity.entity_type == "File":
            # Very basic extraction from SKG Edges if they represent imports
            deps = []
            for edge in context.skg_edges:
                if isinstance(edge, DomainImport):
                    deps.append((f"Uses {edge.raw_statement}", 0.8))
            if deps:
                context.node.relationships.dependencies.extend(deps)
                context.add_provenance('dependencies', 'DependencyEnricher', 0.8, 'Derived from SKG import edges')
        return context
