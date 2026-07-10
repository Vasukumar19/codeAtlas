import os

files = {
    "backend/app/intelligence/prompts/__init__.py": "",
    "backend/app/intelligence/prompts/compressor.py": """
import json
from typing import Dict, Any
from app.retrieval.domain.schemas import ContextPackage

class ContextCompressor:
    def compress(self, package: ContextPackage) -> str:
        # Strip low-confidence nodes, remove bloated data, format as concise JSON
        compressed = {
            "summary": package.repository_summary,
            "entities": [{"id": str(e.node_id), "type": e.entity_type} for e in package.relevant_entities if e.relevance_score > 0.5],
            "routes": [{"id": str(r.node_id), "type": r.entity_type} for r in package.relevant_routes if r.relevance_score > 0.5],
            "paths": package.relevant_graph_paths[:10]  # Cap massive paths
        }
        return json.dumps(compressed)
""",
    "backend/app/intelligence/prompts/builder.py": """
class PromptBuilder:
    def build(self, query: str, compressed_context: str) -> str:
        return f"User Query: {query}\\n\\nContext:\\n{compressed_context}\\n\\nAnswer the query using ONLY the provided context."
""",
    "backend/app/intelligence/strategies/__init__.py": "",
    "backend/app/intelligence/strategies/base.py": """
from abc import ABC, abstractmethod

class ReasoningStrategy(ABC):
    @abstractmethod
    def build_system_instruction(self) -> str:
        pass
""",
    "backend/app/intelligence/strategies/architecture.py": """
from app.intelligence.strategies.base import ReasoningStrategy

class ArchitectureStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "You are an expert software architect. Explain the high-level architecture based ONLY on the provided context."
""",
    "backend/app/intelligence/strategies/impact.py": """
from app.intelligence.strategies.base import ReasoningStrategy

class ImpactAnalysisStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "You are a senior engineer. Explain the blast radius and impact of modifying the components listed in the context."
""",
    "backend/app/intelligence/strategies/execution_flow.py": """
from app.intelligence.strategies.base import ReasoningStrategy

class ExecutionFlowStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "Trace the execution flow step-by-step from entry point to exit point."
""",
    "backend/app/intelligence/strategies/general.py": """
from app.intelligence.strategies.base import ReasoningStrategy

class GeneralStrategy(ReasoningStrategy):
    def build_system_instruction(self) -> str:
        return "You are an expert developer assistant. Answer the question using ONLY the provided context."
""",
    "backend/app/intelligence/strategies/factory.py": """
from app.retrieval.domain.schemas import RetrievalIntent
from app.intelligence.strategies.base import ReasoningStrategy
from app.intelligence.strategies.architecture import ArchitectureStrategy
from app.intelligence.strategies.impact import ImpactAnalysisStrategy
from app.intelligence.strategies.execution_flow import ExecutionFlowStrategy
from app.intelligence.strategies.general import GeneralStrategy

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
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
