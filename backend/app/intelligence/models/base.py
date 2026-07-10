from abc import ABC, abstractmethod

class AIModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_instruction: str) -> str:
        pass
        
    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        pass
