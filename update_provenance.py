import os
import re

# 1. Update schemas.py
schemas_path = "backend/app/enrichment/domain/schemas.py"
with open(schemas_path, "r", encoding="utf-8") as f:
    content = f.read()

if "KnowledgeProvenance" not in content:
    content = content.replace(
        "class KnowledgeIdentity(BaseModel):",
        """from typing import Dict
from datetime import datetime

class KnowledgeProvenance(BaseModel):
    generated_by: str
    generated_at: str
    confidence: float
    evidence: Optional[str] = None

class KnowledgeIdentity(BaseModel):"""
    )
    content = content.replace(
        "    metadata: KnowledgeMetadata = Field(default_factory=KnowledgeMetadata)",
        "    metadata: KnowledgeMetadata = Field(default_factory=KnowledgeMetadata)\n    provenance: Dict[str, KnowledgeProvenance] = Field(default_factory=dict)"
    )
    with open(schemas_path, "w", encoding="utf-8") as f:
        f.write(content)

# 2. Update edge.py
edge_path = "backend/app/models/skg/edge.py"
with open(edge_path, "r", encoding="utf-8") as f:
    content = f.read()
if "provenance:" not in content:
    content = content.replace(
        "    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)",
        "    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)\n    provenance: Mapped[dict] = mapped_column(JSON, default=dict)"
    )
    with open(edge_path, "w", encoding="utf-8") as f:
        f.write(content)

# 3. Update node.py
node_path = "backend/app/models/enrichment/node.py"
with open(node_path, "r", encoding="utf-8") as f:
    content = f.read()
if "provenance:" not in content:
    content = content.replace(
        "    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)",
        "    metadata_: Mapped[dict] = mapped_column(JSON, default=dict)\n    provenance: Mapped[dict] = mapped_column(JSON, default=dict)"
    )
    with open(node_path, "w", encoding="utf-8") as f:
        f.write(content)

# 4. Update SKGBuilder
skg_path = "backend/app/skg/builder.py"
with open(skg_path, "r", encoding="utf-8") as f:
    content = f.read()
if "provenance=" not in content:
    content = content.replace(
        "def _add_edge(self, source_id: uuid.UUID, target_id: uuid.UUID, edge_type: SKGEdgeType, meta: dict = None):",
        "def _add_edge(self, source_id: uuid.UUID, target_id: uuid.UUID, edge_type: SKGEdgeType, meta: dict = None, evidence: str = None):"
    )
    content = content.replace(
        "metadata_=meta or {}",
        "metadata_=meta or {},\n            provenance={\"generated_by\": \"SKGBuilder\", \"evidence\": evidence}"
    )
    # Simple fix for usages
    content = content.replace(
        "self._add_edge(d.parent_id, d.id, SKGEdgeType.CONTAINS)",
        "self._add_edge(d.parent_id, d.id, SKGEdgeType.CONTAINS, evidence='RIM Directory Hierarchy')"
    )
    content = content.replace(
        "self._add_edge(f.directory_id, f.id, SKGEdgeType.CONTAINS)",
        "self._add_edge(f.directory_id, f.id, SKGEdgeType.CONTAINS, evidence='RIM Directory Contains File')"
    )
    content = content.replace(
        "self._add_edge(s.parent_symbol_id, s.id, SKGEdgeType.DECLARES)",
        "self._add_edge(s.parent_symbol_id, s.id, SKGEdgeType.DECLARES, evidence='RIM Symbol Declares Child')"
    )
    content = content.replace(
        "self._add_edge(s.file_id, s.id, SKGEdgeType.CONTAINS)",
        "self._add_edge(s.file_id, s.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Symbol')"
    )
    content = content.replace(
        "self._add_edge(r.file_id, r.id, SKGEdgeType.CONTAINS)",
        "self._add_edge(r.file_id, r.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Route')"
    )
    content = content.replace(
        "self._add_edge(r.id, s.id, SKGEdgeType.ROUTES_TO)",
        "self._add_edge(r.id, s.id, SKGEdgeType.ROUTES_TO, evidence='RIM Route Handler Match')"
    )
    content = content.replace(
        "self._add_edge(i.file_id, i.id, SKGEdgeType.CONTAINS)",
        "self._add_edge(i.file_id, i.id, SKGEdgeType.CONTAINS, evidence='RIM File Contains Import')"
    )
    with open(skg_path, "w", encoding="utf-8") as f:
        f.write(content)

# 5. Update BaseEnricher Context to have add_provenance
base_enrich_path = "backend/app/enrichment/enrichers/base.py"
with open(base_enrich_path, "r", encoding="utf-8") as f:
    content = f.read()
if "def add_provenance" not in content:
    content = content.replace(
        "        self.skg_edges = skg_edges",
        """        self.skg_edges = skg_edges

    def add_provenance(self, field: str, enricher: str, confidence: float, evidence: str = None):
        from datetime import datetime
        from app.enrichment.domain.schemas import KnowledgeProvenance
        self.node.provenance[field] = KnowledgeProvenance(
            generated_by=enricher,
            generated_at=datetime.utcnow().isoformat(),
            confidence=confidence,
            evidence=evidence
        )"""
    )
    with open(base_enrich_path, "w", encoding="utf-8") as f:
        f.write(content)
