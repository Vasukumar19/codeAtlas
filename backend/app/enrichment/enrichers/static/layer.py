from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.rim.domain.models import DomainFile, DomainSymbol


class LayerEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        if isinstance(context.rim_entity, DomainFile):
            path = context.rim_entity.path.lower()
            if "controller" in path or "api" in path or "route" in path:
                context.node.metadata.layer = ("Controller", 0.8)
                context.add_provenance('layer', 'LayerEnricher', 0.8, 'Path matched controller/api/route')
            elif "service" in path:
                context.node.metadata.layer = ("Service", 0.8)
                context.add_provenance('layer', 'LayerEnricher', 0.8, 'Path matched service')
            elif "repo" in path or "model" in path or "db" in path:
                context.node.metadata.layer = ("Repository", 0.8)
                context.add_provenance('layer', 'LayerEnricher', 0.8, 'Path matched repo/model/db')
                
        elif isinstance(context.rim_entity, DomainSymbol):
            name = context.rim_entity.name.lower()
            if "controller" in name:
                context.node.metadata.layer = ("Controller", 0.9)
                context.add_provenance('layer', 'LayerEnricher', 0.9, 'Name matched controller')
            elif "service" in name:
                context.node.metadata.layer = ("Service", 0.9)
                context.add_provenance('layer', 'LayerEnricher', 0.9, 'Name matched service')
        return context
