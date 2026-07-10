from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext


class SummaryEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        # Simple deterministic summary based on purposes and layer
        node = context.node
        if not node.semantics.summary and node.semantics.purposes:
            primary_purpose = node.semantics.purposes[0][0]
            if node.identity.entity_type == "Route":
                node.semantics.summary = (f"Endpoint for {primary_purpose.lower()}.", 0.6)
                context.add_provenance('summary', 'SummaryEnricher', 0.6, 'Endpoint format rule')
            elif node.identity.entity_type == "Class":
                node.semantics.summary = (f"Component handling {primary_purpose.lower()}.", 0.6)
                context.add_provenance('summary', 'SummaryEnricher', 0.6, 'Component format rule')
            elif node.identity.entity_type == "Function":
                node.semantics.summary = (f"Function executing {primary_purpose.lower()}.", 0.6)
                context.add_provenance('summary', 'SummaryEnricher', 0.6, 'Function format rule')
        return context
