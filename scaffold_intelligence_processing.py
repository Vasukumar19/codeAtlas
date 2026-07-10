import os

files = {
    "backend/app/intelligence/response/__init__.py": "",
    "backend/app/intelligence/response/validator.py": """
import json
from app.retrieval.domain.schemas import ContextPackage

class ResponseValidator:
    def validate(self, raw_response: str, context: ContextPackage) -> bool:
        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError:
            return False
            
        # Extract cited node_ids
        cited_ids = set()
        for citation in data.get("citations", []):
            if "node_id" in citation:
                cited_ids.add(str(citation["node_id"]))
                
        # Valid nodes from context
        valid_ids = set()
        for e in context.relevant_entities:
            valid_ids.add(str(e.node_id))
        for r in context.relevant_routes:
            valid_ids.add(str(r.node_id))
        for p in context.relevant_graph_paths:
            valid_ids.add(p)
            
        # Check for hallucinations
        for cid in cited_ids:
            if cid not in valid_ids:
                return False
                
        return True
""",
    "backend/app/intelligence/response/formatter.py": """
import json
from app.intelligence.domain.schemas import StructuredAIResponse

class ResponseFormatter:
    def format(self, raw_response: str) -> StructuredAIResponse:
        data = json.loads(raw_response)
        return StructuredAIResponse(**data)
""",
    "backend/app/intelligence/session/__init__.py": "",
    "backend/app/intelligence/session/manager.py": """
from typing import List, Dict, Any

class ConversationManager:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        
    def add_turn(self, query: str, response: str):
        self.history.append({"query": query, "response": response})
""",
    "backend/app/intelligence/observability.py": """
import time

class Observability:
    @staticmethod
    def log(model: str, prompt_size: int, latency_ms: int):
        # Mock logging
        print(f"Model: {model}, Prompt Size: {prompt_size}, Latency: {latency_ms}ms")
""",
    "backend/app/intelligence/gateway.py": """
import time
from app.retrieval.domain.schemas import ContextPackage, RetrievalIntent
from app.intelligence.strategies.factory import StrategyFactory
from app.intelligence.prompts.compressor import ContextCompressor
from app.intelligence.prompts.builder import PromptBuilder
from app.intelligence.models.registry import ModelRegistry
from app.intelligence.response.validator import ResponseValidator
from app.intelligence.response.formatter import ResponseFormatter
from app.intelligence.session.manager import ConversationManager
from app.intelligence.observability import Observability
from app.intelligence.domain.schemas import StructuredAIResponse

class AIGateway:
    def __init__(self):
        self.compressor = ContextCompressor()
        self.builder = PromptBuilder()
        self.validator = ResponseValidator()
        self.formatter = ResponseFormatter()
        self.session = ConversationManager()
        
    async def process(self, query: str, context: ContextPackage, intent: RetrievalIntent, model_name: str = "Gemini") -> StructuredAIResponse:
        start_time = time.time()
        
        # 1. Strategy
        strategy = StrategyFactory.get_strategy(intent)
        sys_inst = strategy.build_system_instruction()
        
        # 2. Compress
        compressed_ctx = self.compressor.compress(context)
        
        # 3. Build Prompt
        prompt = self.builder.build(query, compressed_ctx)
        
        # 4. Invoke Model
        provider = ModelRegistry.get(model_name)
        if not provider:
            raise ValueError(f"Provider {model_name} not found")
            
        raw_response = await provider.generate(prompt, sys_inst)
        
        latency = int((time.time() - start_time) * 1000)
        Observability.log(model_name, len(prompt), latency)
        
        # 5. Validate
        if not self.validator.validate(raw_response, context):
            raise ValueError("LLM Hallucination Detected: Invalid node cited.")
            
        # 6. Format
        structured_response = self.formatter.format(raw_response)
        
        # 7. Session
        self.session.add_turn(query, raw_response)
        
        return structured_response
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
