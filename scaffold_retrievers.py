import os

files = {
    "backend/app/retrieval/retrievers/__init__.py": "",
    "backend/app/retrieval/retrievers/base.py": """
from abc import ABC, abstractmethod
from typing import List
from app.retrieval.domain.schemas import UserQuery, RetrievalResult

class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        pass
""",
    "backend/app/retrieval/registry.py": """
from typing import Dict, Type
from app.retrieval.retrievers.base import BaseRetriever

class RetrievalRegistry:
    _retrievers: Dict[str, BaseRetriever] = {}
    
    @classmethod
    def register(cls, name: str, retriever: BaseRetriever):
        cls._retrievers[name] = retriever
        
    @classmethod
    def get(cls, name: str) -> BaseRetriever:
        return cls._retrievers.get(name)
""",
    "backend/app/retrieval/retrievers/graph.py": """
import uuid
from typing import List
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult

class GraphRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        # Mock Graph Retrieval
        return [
            RetrievalResult(
                node_id=uuid.uuid4(),
                entity_type="GraphPath",
                relevance_score=0.9,
                evidence=["Graph traversal from Service to Repository"]
            )
        ]
""",
    "backend/app/retrieval/retrievers/vector.py": """
import uuid
from typing import List
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult

class VectorRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        # Mock FAISS Retrieval
        return [
            RetrievalResult(
                node_id=uuid.uuid4(),
                entity_type="Function",
                relevance_score=0.85,
                evidence=["FAISS similarity search"]
            )
        ]
""",
    "backend/app/retrieval/retrievers/metadata.py": """
import uuid
from typing import List
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult

class MetadataRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        # Mock PostgreSQL Retrieval
        return [
            RetrievalResult(
                node_id=uuid.uuid4(),
                entity_type="Class",
                relevance_score=0.7,
                evidence=["Metadata exact match"]
            )
        ]
""",
    "backend/app/retrieval/retrievers/route.py": """
import uuid
from typing import List
from app.retrieval.retrievers.base import BaseRetriever, UserQuery, RetrievalResult

class RouteRetriever(BaseRetriever):
    async def retrieve(self, query: UserQuery) -> List[RetrievalResult]:
        # Mock Route Retrieval
        return [
            RetrievalResult(
                node_id=uuid.uuid4(),
                entity_type="Route",
                relevance_score=0.95,
                evidence=["Matched endpoint path"]
            )
        ]
""",
    "backend/app/retrieval/retrievers/function.py": """
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
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
