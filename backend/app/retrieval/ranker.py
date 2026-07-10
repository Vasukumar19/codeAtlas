
from app.retrieval.domain.schemas import RetrievalResult


class ContextRanker:
    def rank(self, results: list[RetrievalResult]) -> list[RetrievalResult]:
        # Sort by relevance_score descending
        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
