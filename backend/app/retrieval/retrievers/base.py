from abc import ABC, abstractmethod
from typing import List
from app.retrieval.domain.schemas import UserQuery, RetrievalResult

class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        pass
