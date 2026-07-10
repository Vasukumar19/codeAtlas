from app.intelligence.strategies.base import ReasoningStrategy


class GeneralStrategy(ReasoningStrategy):
    @property
    def response_type(self) -> str:
        return "General Explanation"

    @property
    def response_title(self) -> str:
        return "Analysis & Explanation"

    @property
    def requires_team(self) -> bool:
        return True

    def get_specific_instructions(self) -> str:
        return "Answer the user's question clearly. Consider multiple perspectives (Architecture, Quality, Security) where applicable."
