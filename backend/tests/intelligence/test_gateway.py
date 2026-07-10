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

@pytest.mark.asyncio
async def test_ai_gateway():
    gateway = AIGateway()
    
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
    response = await gateway.process("Explain architecture", context, RetrievalIntent.ARCHITECTURE)
    
    assert response.title == "Architecture Overview"
    assert len(response.sections) > 0
    # Our mock injects citations if it sees a UUID in the prompt
    assert len(response.citations) > 0
    assert str(response.citations[0].node_id) == str(node_id)
    
    # 2.5 Test OpenAI Strategy
    response_openai = await gateway.process("Explain architecture", context, RetrievalIntent.ARCHITECTURE, model_name="OpenAI")
    assert response_openai.title == "Architecture Overview (OpenAI)"
    assert len(response_openai.sections) > 0
    assert len(response_openai.citations) > 0
    assert str(response_openai.citations[0].node_id) == str(node_id)
    
    # 3. Test Hallucination Rejection
    # We will pass an empty context. The LLM will still try to cite the node_id (if we force it),
    # but the mock provider only pulls UUIDs from the prompt.
    # So let's create a custom provider that hallucinates a node_id
    class HallucinatingProvider(GeminiProvider):
        async def generate(self, prompt, sys):
            import json
            resp = {
                "type": "Test", "title": "Test", "summary": "Test",
                "sections": [], "steps": [], "confidence": 0.9, "metadata": {},
                "citations": [{"node_id": str(uuid.uuid4()), "confidence": 0.9}]
            }
            return json.dumps(resp)
            
    ModelRegistry.register("HallucinatingModel", HallucinatingProvider())
    
    with pytest.raises(ValueError, match="LLM Hallucination Detected"):
        await gateway.process("Test", context, RetrievalIntent.ARCHITECTURE, model_name="HallucinatingModel")
