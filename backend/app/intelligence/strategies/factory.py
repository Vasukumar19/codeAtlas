from app.intelligence.strategies.architecture import ArchitectureStrategy
from app.intelligence.strategies.base import ReasoningStrategy
from app.intelligence.strategies.execution_flow import ExecutionFlowStrategy
from app.intelligence.strategies.general import GeneralStrategy
from app.intelligence.strategies.impact import ImpactAnalysisStrategy
from app.retrieval.domain.schemas import RetrievalIntent


class StrategyFactory:
    @staticmethod
    def get_strategy(intent: RetrievalIntent) -> ReasoningStrategy:
        if intent == RetrievalIntent.ARCHITECTURE:
            return ArchitectureStrategy()
        elif intent == RetrievalIntent.IMPACT_ANALYSIS:
            return ImpactAnalysisStrategy()
        elif intent == RetrievalIntent.EXECUTION_FLOW:
            return ExecutionFlowStrategy()
        else:
            return GeneralStrategy()
