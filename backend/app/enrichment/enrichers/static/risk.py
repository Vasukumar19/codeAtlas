from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext


class RiskEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        # Basic heuristic: if it has lots of TODOs in metadata, higher risk.
        # But since RIM Entity doesn't store all TODOs except at file level,
        # we do a simple deterministic assignment.
        ent = context.rim_entity
        todos = ent.metadata.get("total_todos", 0)
        
        if todos > 5:
            context.node.metrics.risk_level = ("High", 0.7)
            context.add_provenance('risk_level', 'RiskEnricher', 0.7, 'TODO count > 5')
        elif todos > 0:
            context.node.metrics.risk_level = ("Medium", 0.7)
            context.add_provenance('risk_level', 'RiskEnricher', 0.7, 'TODO count > 0')
        else:
            context.node.metrics.risk_level = ("Low", 0.4)
            context.add_provenance('risk_level', 'RiskEnricher', 0.4, 'No TODOs found')
            
        return context
