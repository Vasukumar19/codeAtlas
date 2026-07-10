from app.intelligence.strategies.base import ReasoningStrategy


class ArchitectureStrategy(ReasoningStrategy):
    @property
    def response_type(self) -> str:
        return "Architecture Explanation"

    @property
    def response_title(self) -> str:
        return "Architecture Overview"

    def get_specific_instructions(self) -> str:
        return "Focus on the high-level architecture. Identify major layers, components, and design patterns."
