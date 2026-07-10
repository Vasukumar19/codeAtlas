import os

files = {
    "backend/app/enrichment/enrichers/__init__.py": "",
    "backend/app/enrichment/enrichers/base.py": """
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from app.enrichment.domain.schemas import KnowledgeNode
from app.rim.domain.models import DomainEntity

class KnowledgeContext:
    def __init__(self, node: KnowledgeNode, rim_entity: DomainEntity, skg_edges: List[Any]):
        self.node = node
        self.rim_entity = rim_entity
        self.skg_edges = skg_edges

class BaseEnricher(ABC):
    @abstractmethod
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        pass
""",
    "backend/app/enrichment/enrichers/static/__init__.py": "",
    "backend/app/enrichment/enrichers/static/framework.py": """
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
                        break
                    elif "express" in stmt:
                        context.node.metadata.framework = ("Express", 0.9)
                        break
                    elif "spring" in stmt:
                        context.node.metadata.framework = ("Spring Boot", 0.9)
                        break
        return context
""",
    "backend/app/enrichment/enrichers/static/layer.py": """
from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext
from app.rim.domain.models import DomainFile, DomainSymbol

class LayerEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        if isinstance(context.rim_entity, DomainFile):
            path = context.rim_entity.path.lower()
            if "controller" in path or "api" in path or "route" in path:
                context.node.metadata.layer = ("Controller", 0.8)
            elif "service" in path:
                context.node.metadata.layer = ("Service", 0.8)
            elif "repo" in path or "model" in path or "db" in path:
                context.node.metadata.layer = ("Repository", 0.8)
                
        elif isinstance(context.rim_entity, DomainSymbol):
            name = context.rim_entity.name.lower()
            if "controller" in name:
                context.node.metadata.layer = ("Controller", 0.9)
            elif "service" in name:
                context.node.metadata.layer = ("Service", 0.9)
        return context
""",
    "backend/app/enrichment/enrichers/static/purpose.py": """
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
            
        return context
""",
    "backend/app/enrichment/enrichers/static/summary.py": """
from app.enrichment.enrichers.base import BaseEnricher, KnowledgeContext

class SummaryEnricher(BaseEnricher):
    async def enrich(self, context: KnowledgeContext) -> KnowledgeContext:
        # Simple deterministic summary based on purposes and layer
        node = context.node
        if not node.semantics.summary and node.semantics.purposes:
            primary_purpose = node.semantics.purposes[0][0]
            if node.identity.entity_type == "Route":
                node.semantics.summary = (f"Endpoint for {primary_purpose.lower()}.", 0.6)
            elif node.identity.entity_type == "Class":
                node.semantics.summary = (f"Component handling {primary_purpose.lower()}.", 0.6)
            elif node.identity.entity_type == "Function":
                node.semantics.summary = (f"Function executing {primary_purpose.lower()}.", 0.6)
        return context
""",
    "backend/app/enrichment/enrichers/static/risk.py": """
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
        elif todos > 0:
            context.node.metrics.risk_level = ("Medium", 0.7)
        else:
            context.node.metrics.risk_level = ("Low", 0.4)
            
        return context
""",
    "backend/app/enrichment/enrichers/static/dependencies.py": """
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
        return context
""",
    "backend/app/enrichment/pipeline.py": """
from typing import List
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
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
