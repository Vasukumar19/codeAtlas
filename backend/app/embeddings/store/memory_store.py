from typing import List
from app.embeddings.store.base import VectorStore

class MemoryVectorStore(VectorStore):
    def __init__(self, collection_name: str, dimension: int):
        self.collection_name = collection_name
        self.dimension = dimension
        self.vectors = []
        self.ids = []
        
    def add(self, vectors: List[List[float]], ids: List[str]):
        if len(vectors) != len(ids):
            raise ValueError("Vectors and ids must have the same length")
        for v in vectors:
            if len(v) != self.dimension:
                raise ValueError(f"Expected dimension {self.dimension}, got {len(v)}")
        self.vectors.extend(vectors)
        self.ids.extend(ids)
        
    def save(self):
        # In a real memory store we might pickle this or persist to a file.
        # But this is primarily an agnostic test provider.
        pass
