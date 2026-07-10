
class CapabilityRegistry:
    _capabilities: dict[str, dict[str, bool]] = {}

    @classmethod
    def register(cls, language: str, capabilities: dict[str, bool]):
        cls._capabilities[language] = capabilities

    @classmethod
    def get(cls, language: str) -> dict[str, bool]:
        return cls._capabilities.get(language, {})
