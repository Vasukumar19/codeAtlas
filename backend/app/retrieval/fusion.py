import uuid

from app.retrieval.domain.schemas import RetrievalResult


class ResultFusion:
    def fuse(self, results_lists: list[list[RetrievalResult]]) -> list[RetrievalResult]:
        fused_map: dict[uuid.UUID, RetrievalResult] = {}
        
        for results in results_lists:
            if not results:
                continue
            for r in results:
                if r.node_id in fused_map:
                    # Merge evidence and boost score
                    existing = fused_map[r.node_id]
                    existing.evidence.extend([e for e in r.evidence if e not in existing.evidence])
                    existing.relevance_score = min(1.0, existing.relevance_score + (r.relevance_score * 0.2))
                else:
                    fused_map[r.node_id] = r
                    
        return list(fused_map.values())
