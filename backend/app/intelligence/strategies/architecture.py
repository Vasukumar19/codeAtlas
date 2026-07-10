from app.intelligence.strategies.base import ReasoningStrategy

class ArchitectureStrategy(ReasoningStrategy):
    def get_specific_instructions(self) -> str:
        return "Focus on the high-level architecture. Identify major layers, components, and design patterns. Set type to 'Architecture Explanation'."
