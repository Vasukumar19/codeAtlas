import os

files = {
    "backend/app/intelligence/__init__.py": "",
    "backend/app/intelligence/domain/__init__.py": "",
    "backend/app/intelligence/domain/schemas.py": """
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid

class AICitation(BaseModel):
    node_id: uuid.UUID
    file_path: Optional[str] = None
    symbol_name: Optional[str] = None
    confidence: float

class AIResponseSection(BaseModel):
    title: str
    content: str

class StructuredAIResponse(BaseModel):
    type: str
    title: str
    summary: str
    sections: List[AIResponseSection] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    citations: List[AICitation] = Field(default_factory=list)
    confidence: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
""",
    "backend/app/intelligence/models/__init__.py": "",
    "backend/app/intelligence/models/base.py": """
from abc import ABC, abstractmethod

class AIModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_instruction: str) -> str:
        pass
""",
    "backend/app/intelligence/models/registry.py": """
from typing import Dict, Type
from app.intelligence.models.base import AIModelProvider

class ModelRegistry:
    _providers: Dict[str, AIModelProvider] = {}
    
    @classmethod
    def register(cls, name: str, provider: AIModelProvider):
        cls._providers[name] = provider
        
    @classmethod
    def get(cls, name: str) -> AIModelProvider:
        return cls._providers.get(name)
""",
    "backend/app/intelligence/models/gemini.py": """
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
"""
}

for path, content in files.items():
    full_path = os.path.join("c:/Users/kumar/project/codeAtlas", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
