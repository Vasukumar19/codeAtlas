import uuid
from typing import List
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult

class FunctionRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        return [
            RetrievalResult(
                node_id=uuid.uuid4(),
                entity_type="Function",
                relevance_score=0.8,
                evidence=["Matched function signature"]
            )
        ]
