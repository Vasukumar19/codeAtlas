import pytest
import uuid
from app.retrieval.domain.schemas import ContextPackage, RetrievalIntent, RetrievalResult
from app.intelligence.gateway import AIGateway
from app.intelligence.models.registry import ModelRegistry
from app.intelligence.models.gemini import GeminiProvider
from app.intelligence.models.openai import OpenAIProvider

@pytest.fixture(autouse=True)
def setup_registry():
    ModelRegistry.register("Gemini", GeminiProvider())
    ModelRegistry.register("OpenAI", OpenAIProvider())

class MockConversationManager:
    def __init__(self):
        self.history = []
    async def get_history(self, repository_id):
        return self.history
    async def add_turn(self, repository_id, query, response):
        self.history.append({"query": query, "response": response})

@pytest.mark.asyncio
async def test_ai_gateway():
    gateway = AIGateway(MockConversationManager())
    
    # 1. Mock Context Package
    node_id = uuid.uuid4()
    context = ContextPackage(
        repository_summary="Test Repo",
        relevant_entities=[
            RetrievalResult(node_id=node_id, entity_type="Function", relevance_score=0.9, evidence=[])
        ]
    )
    
    # 2. Test Architecture Strategy
    # The provider is mocked to return a JSON string with a citation to the injected node_id
    repo_id = uuid.uuid4()
    response = await gateway.process("Explain architecture", context, RetrievalIntent.ARCHITECTURE, repository_id=repo_id)
    
    assert response.title == "Architecture Overview"
    assert response.type == "Architecture Explanation"
    assert len(response.citations) > 0
    assert str(response.citations[0].node_id) == str(node_id)
    
    # 3. Test Impact Analysis Strategy
    resp_impact = await gateway.process("What breaks if I change this?", context, RetrievalIntent.IMPACT_ANALYSIS, repository_id=repo_id)
    assert resp_impact.title == "Impact & Dependencies"
    assert resp_impact.type == "Impact Analysis"
    
    # 4. Test Execution Flow Strategy
    resp_flow = await gateway.process("How does this run?", context, RetrievalIntent.EXECUTION_FLOW, repository_id=repo_id)
    assert resp_flow.title == "Execution Path"
    assert resp_flow.type == "Execution Flow"
    
    # 5. Test General Strategy (Team Orchestrator)
    resp_general = await gateway.process("Explain the repo", context, RetrievalIntent.GENERAL_QUESTION, repository_id=repo_id)
    assert resp_general.title == "Analysis & Explanation"
    assert resp_general.type == "General Explanation"
    
    # We removed strict JSON hallucination validation in favor of markdown response,
    # so we don't test hallucination rejection here anymore.
