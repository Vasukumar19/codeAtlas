from abc import ABC, abstractmethod
from typing import List

class VectorStore(ABC):
    @abstractmethod
    def add(self, vectors: List[List[float]], ids: List[str]):
        pass
        
    @abstractmethod
    def save(self):
        pass
