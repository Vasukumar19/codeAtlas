from app.intelligence.strategies.base import ReasoningStrategy

class GeneralStrategy(ReasoningStrategy):
    def get_specific_instructions(self) -> str:
        return "Answer the user's question clearly. Set type to 'General Explanation'."
