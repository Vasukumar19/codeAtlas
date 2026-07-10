from app.intelligence.strategies.base import ReasoningStrategy


class ExecutionFlowStrategy(ReasoningStrategy):
    @property
    def response_type(self) -> str:
        return "Execution Flow"

    @property
    def response_title(self) -> str:
        return "Execution Path"

    def get_specific_instructions(self) -> str:
        return "Trace the execution path of the request. Outline the steps clearly in the 'steps' JSON array."
