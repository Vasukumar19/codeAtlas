from typing import List
from app.embeddings.providers.base import EmbeddingProvider
# NOTE: sentence-transformers is heavy, we'll mock it for now
# import sentence_transformers

class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._dimension = 384
        # self.model = sentence_transformers.SentenceTransformer(model_name)

    @property
    def model_name(self) -> str:
        return self._model_name
        
    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Mock embedding since we don't want to load PyTorch during basic tests
        # In production this would be: return self.model.encode(texts).tolist()
        return [[0.1] * self.dimension for _ in texts]
