from abc import ABC, abstractmethod
from typing import Any

from app.enrichment.domain.schemas import KnowledgeNode
from app.rim.domain.models import DomainEntity


class KnowledgeContext:
    def __init__(self, node: KnowledgeNode, rim_entity: DomainEntity, skg_edges: list[Any]):
        self.node = node
        self.rim_entity = rim_entity
        self.skg_edges = skg_edges

    def add_provenance(self, field: str, enricher: str, confidence: float, evidence: str = None):
        from datetime import datetime

        from app.enrichment.domain.schemas import KnowledgeProvenance
        self.node.provenance[field] = KnowledgeProvenance(
            generated_by=enricher,
            generated_at=datetime.utcnow().isoformat(),
            confidence=confidence,
            evidence=evidence
        )

class BaseEnricher(ABC):
    @abstractmethod
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        pass
