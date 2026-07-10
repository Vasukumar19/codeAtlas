from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.retrieval.domain.schemas import UserQuery, RetrievalResult

class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> List[RetrievalResult]:
        pass
