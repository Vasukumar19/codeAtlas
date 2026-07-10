import json
from typing import Dict, Any
from app.retrieval.domain.schemas import ContextPackage

class ContextCompressor:
    def compress(self, package: ContextPackage) -> str:
        # Strip low-confidence nodes, remove bloated data, format as concise JSON
        compressed = {
            "summary": package.repository_summary,
            "entities": [{"id": str(e.node_id), "type": e.entity_type} for e in package.relevant_entities if e.relevance_score > 0.5],
            "routes": [{"id": str(r.node_id), "type": r.entity_type} for r in package.relevant_routes if r.relevance_score > 0.5],
            "paths": package.relevant_graph_paths[:10]  # Cap massive paths
        }
        return json.dumps(compressed)
