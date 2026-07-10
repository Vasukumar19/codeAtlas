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
        
    async def process(self, query: str, context: ContextPackage, intent: RetrievalIntent, model_name: str = "OpenAI") -> StructuredAIResponse:
        start_time = time.time()
        
        # 1. Strategy
        strategy = StrategyFactory.get_strategy(intent)
        sys_inst = strategy.build_system_instruction()
        
        # 2. Compress
        compressed_ctx = self.compressor.compress(context)
        
        # 3. Build Prompt
        prompt = self.builder.build(query, compressed_ctx)
        
        # 4. Invoke Multi-Agent Team
        from app.intelligence.agents.orchestrator import TeamOrchestrator
        orchestrator = TeamOrchestrator()
        
        raw_response = await orchestrator.orchestrate(prompt, context, model_name)
        
        latency = int((time.time() - start_time) * 1000)
        Observability.log(model_name, len(prompt), latency)
        
        # 5. Format to StructuredAIResponse
        structured_response = StructuredAIResponse(
            type="Orchestrator Analysis",
            title="AI Team Insights",
            summary=raw_response,
            confidence=0.95
        )
        
        # 6. Session
        self.session.add_turn(query, raw_response)
        
        return structured_response
