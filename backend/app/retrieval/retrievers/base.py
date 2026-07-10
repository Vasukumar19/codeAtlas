from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.retrieval.domain.schemas import RetrievalResult, UserQuery


class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: UserQuery, db: AsyncSession) -> list[RetrievalResult]:
        pass
