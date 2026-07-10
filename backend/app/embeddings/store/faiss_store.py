from typing import List
from app.embeddings.store.base import VectorStore
# import faiss

class FaissStore(VectorStore):
    def __init__(self, collection_name: str, dimension: int):
        self.collection_name = collection_name
        self.dimension = dimension
        self.storage_path = f"{collection_name}.faiss"
        # self.index = faiss.IndexFlatL2(dimension)
        
    def add(self, vectors: List[List[float]], ids: List[str]):
        # Mock add
        pass
        
    def save(self):
        # Mock save
        pass
