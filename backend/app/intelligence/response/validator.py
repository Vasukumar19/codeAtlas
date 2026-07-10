import json
from app.retrieval.domain.schemas import ContextPackage

class ResponseValidator:
    def validate(self, raw_response: str, context: ContextPackage) -> bool:
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            return False
            
        # Extract cited node_ids
        cited_ids = set()
        for citation in data.get("citations", []):
            if "node_id" in citation:
                cited_ids.add(str(citation["node_id"]))
                
        # Valid nodes from context
        valid_ids = set()
        for e in context.relevant_entities:
            valid_ids.add(str(e.node_id))
        for r in context.relevant_routes:
            valid_ids.add(str(r.node_id))
        for p in context.relevant_graph_paths:
            valid_ids.add(p)
            
        # Check for hallucinations
        for cid in cited_ids:
            if cid not in valid_ids:
                return False
                
        return True
