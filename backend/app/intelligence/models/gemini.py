import json
from app.intelligence.models.base import AIModelProvider

class GeminiProvider(AIModelProvider):
    async def generate(self, prompt: str, system_instruction: str) -> str:
        # Mock Gemini Network Call
        # Returns a JSON string matching StructuredAIResponse
        response = {
            "type": "Architecture Explanation",
            "title": "Architecture Overview",
            "summary": "This repository uses a layered architecture.",
            "sections": [
                {"title": "Core Components", "content": "Controller, Service, Repository."}
            ],
            "steps": [],
            "citations": [],
            "confidence": 0.95,
            "metadata": {}
        }
        
        # Simple heuristic to extract cited nodes from prompt to simulate LLM citation
        import re
        node_ids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', prompt)
        if node_ids:
            response["citations"] = [
                {"node_id": node_id, "confidence": 0.9} for node_id in set(node_ids)
            ]
            
        return json.dumps(response)
