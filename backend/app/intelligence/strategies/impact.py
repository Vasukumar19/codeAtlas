from app.intelligence.strategies.base import ReasoningStrategy

class ImpactAnalysisStrategy(ReasoningStrategy):
    def get_specific_instructions(self) -> str:
        return "Focus on identifying downstream dependencies. List services and files affected by changes. Set type to 'Impact Analysis'."
