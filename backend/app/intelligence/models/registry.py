from typing import Dict, Type
from app.intelligence.models.base import AIModelProvider

class ModelRegistry:
    _providers: Dict[str, AIModelProvider] = {}
    
    @classmethod
    def register(cls, name: str, provider: AIModelProvider):
        cls._providers[name] = provider
        
    @classmethod
    def get(cls, name: str) -> AIModelProvider:
        return cls._providers.get(name)
