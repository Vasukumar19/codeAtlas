from app.intelligence.strategies.base import ReasoningStrategy

class ExecutionFlowStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "Trace the execution flow step-by-step from entry point to exit point."
