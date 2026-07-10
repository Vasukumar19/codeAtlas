from typing import Dict, Type, Any
from app.parser.capabilities import CapabilityRegistry

class ParserRegistry:
    _plugins: Dict[str, Type] = {}

    @classmethod
    def register(cls, language: str, plugin_class: Type, capabilities: Dict[str, bool]):
        cls._plugins[language] = plugin_class
        CapabilityRegistry.register(language, capabilities)

    @classmethod
    def get_plugin(cls, language: str) -> Type | None:
        return cls._plugins.get(language)
    
    @classmethod
    def list_supported_languages(cls) -> list[str]:
        return list(cls._plugins.keys())
