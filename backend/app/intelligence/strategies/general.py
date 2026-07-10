from app.intelligence.strategies.base import ReasoningStrategy

class GeneralStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "You are an expert developer assistant. Answer the question using ONLY the provided context."
