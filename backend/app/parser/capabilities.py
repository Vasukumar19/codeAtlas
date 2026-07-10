from typing import Dict, Any

class CapabilityRegistry:
    _capabilities: Dict[str, Dict[str, bool]] = {}

    @classmethod
    def register(cls, language: str, capabilities: Dict[str, bool]):
        cls._capabilities[language] = capabilities

    @classmethod
    def get(cls, language: str) -> Dict[str, bool]:
        return cls._capabilities.get(language, {})
