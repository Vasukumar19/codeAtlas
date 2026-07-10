import time

from app.intelligence.domain.schemas import StructuredAIResponse
from app.intelligence.observability import Observability
from app.intelligence.prompts.builder import PromptBuilder
from app.intelligence.prompts.compressor import ContextCompressor
from app.intelligence.response.formatter import ResponseFormatter
from app.intelligence.response.validator import ResponseValidator
from app.intelligence.session.manager import ConversationManager
from app.intelligence.strategies.factory import StrategyFactory
from app.retrieval.domain.schemas import ContextPackage, RetrievalIntent


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
        
        # 4. Invoke model
        if strategy.requires_team:
            from app.intelligence.agents.orchestrator import TeamOrchestrator
            orchestrator = TeamOrchestrator()
            raw_response = await orchestrator.orchestrate(prompt, context, model_name, strategy_focus=sys_inst)
        else:
            from app.intelligence.models.registry import ModelRegistry
            provider = ModelRegistry.get(model_name)
            if not provider:
                raise ValueError(f"Provider {model_name} not found")
            raw_response = await provider.generate(prompt, sys_inst)
        
        latency = int((time.time() - start_time) * 1000)
        Observability.log(model_name, len(prompt), latency)
        
        # 5. Extract citations from context
        from app.intelligence.domain.schemas import AICitation
        citations = []
        for ent in context.relevant_entities:
            citations.append(AICitation(
                node_id=ent.node_id,
                file_path=ent.file_path if hasattr(ent, 'file_path') else None,
                symbol_name=ent.entity_name if hasattr(ent, 'entity_name') else None,
                confidence=ent.relevance_score
            ))

        # 6. Format to StructuredAIResponse
        structured_response = StructuredAIResponse(
            type=strategy.response_type,
            title=strategy.response_title,
            summary=raw_response,
            citations=citations,
            confidence=0.95
        )
        
        # 6. Session
        self.session.add_turn(query, raw_response)
        
        return structured_response
