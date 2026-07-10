from app.intelligence.strategies.base import ReasoningStrategy

class ExecutionFlowStrategy(ReasoningStrategy):
    def get_specific_instructions(self) -> str:
        return "Trace the execution path of the request. Outline the steps clearly in the 'steps' JSON array. Set type to 'Execution Flow'."
