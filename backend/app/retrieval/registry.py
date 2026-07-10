from app.retrieval.retrievers.base import BaseRetriever


class RetrievalRegistry:
    _retrievers: dict[str, BaseRetriever] = {}
    
    @classmethod
    def register(cls, name: str, retriever: BaseRetriever):
        cls._retrievers[name] = retriever
        
    @classmethod
    def get(cls, name: str) -> BaseRetriever:
        return cls._retrievers.get(name)
