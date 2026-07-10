import uuid
from typing import List, Any
from app.enrichment.enrichers.base import KnowledgeContext, BaseEnricher
from app.enrichment.domain.schemas import KnowledgeNode, KnowledgeIdentity
from app.rim.domain.models import DomainEntity

class KnowledgePipeline:
    def __init__(self, enrichers: List[BaseEnricher] = None):
        if enrichers is None:
            # Default static enrichers
            from app.enrichment.enrichers.static.framework import FrameworkEnricher
            from app.enrichment.enrichers.static.layer import LayerEnricher
            from app.enrichment.enrichers.static.purpose import PurposeEnricher
            from app.enrichment.enrichers.static.summary import SummaryEnricher
            from app.enrichment.enrichers.static.risk import RiskEnricher
            from app.enrichment.enrichers.static.dependencies import DependencyEnricher
            
            self.enrichers = [
                FrameworkEnricher(),
                LayerEnricher(),
                PurposeEnricher(),
                DependencyEnricher(),
                SummaryEnricher(), # Needs purpose first
                RiskEnricher()
            ]
        else:
            self.enrichers = enrichers
            
    async def execute(self, rim_entity: DomainEntity, entity_type: str, skg_edges: List[Any], skg_node_id: uuid.UUID = None) -> KnowledgeNode:
        import uuid
        identity = KnowledgeIdentity(
            id=uuid.uuid4(),
            entity_type=entity_type,
            repository_id=rim_entity.repository_id,
            repository_version_id=rim_entity.repository_version_id,
            rim_entity_id=rim_entity.id,
            skg_node_id=skg_node_id
        )
        
        node = KnowledgeNode(identity=identity)
        context = KnowledgeContext(node, rim_entity, skg_edges)
        
        for enricher in self.enrichers:
            context = await enricher.enrich(context)
            
        return context.node
