from app.intelligence.strategies.base import ReasoningStrategy


class ImpactAnalysisStrategy(ReasoningStrategy):
    @property
    def response_type(self) -> str:
        return "Impact Analysis"

    @property
    def response_title(self) -> str:
        return "Impact & Dependencies"

    def get_specific_instructions(self) -> str:
        return "Focus on identifying downstream dependencies. List services and files affected by changes."
