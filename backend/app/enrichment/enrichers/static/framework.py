from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.rim.domain.models import DomainImport

class FrameworkEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        if context.node.identity.entity_type == "Repository":
            for edge in context.skg_edges:
                if getattr(edge, 'raw_statement', None):
                    stmt = edge.raw_statement.lower()
                    if "fastapi" in stmt:
                        context.node.metadata.framework = ("FastAPI", 0.9)
                        context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Found fastapi import')
                        break
                    elif "express" in stmt:
                        context.node.metadata.framework = ("Express", 0.9)
                        context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Found express import')
                        break
                    elif "spring" in stmt:
                        context.node.metadata.framework = ("Spring Boot", 0.9)
                        context.add_provenance('framework', 'FrameworkEnricher', 0.9, 'Found spring import')
                        break
        return context
