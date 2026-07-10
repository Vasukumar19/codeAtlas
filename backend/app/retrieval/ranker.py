from typing import List
from app.retrieval.domain.schemas import RetrievalResult

class ContextRanker:
    def rank(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        # Sort by relevance_score descending
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
