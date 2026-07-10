from app.intelligence.strategies.base import ReasoningStrategy

class ImpactAnalysisStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "You are a senior engineer. Explain the blast radius and impact of modifying the components listed in the context."
