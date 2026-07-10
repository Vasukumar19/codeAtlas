from app.intelligence.strategies.base import ReasoningStrategy

class ArchitectureStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "You are an expert software architect. Explain the high-level architecture based ONLY on the provided context."
