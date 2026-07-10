from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.rim.domain.models import DomainRoute, DomainSymbol


class PurposeEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        ent = context.rim_entity
        purposes = []
        if isinstance(ent, DomainRoute):
            if "auth" in ent.path.lower() or "login" in ent.path.lower():
                purposes.append(("Authentication", 0.9))
                purposes.append(("API", 0.7))
        elif isinstance(ent, DomainSymbol):
            if "login" in ent.name.lower() or "auth" in ent.name.lower():
                purposes.append(("Authentication", 0.8))
                
        if purposes:
            context.node.semantics.purposes.extend(purposes)
            context.add_provenance('purposes', 'PurposeEnricher', purposes[0][1], 'Name/Path heuristics match')
            
        return context
