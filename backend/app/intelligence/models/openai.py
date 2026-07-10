import os

import httpx

from app.intelligence.models.base import AIModelProvider


class OpenAIProvider(AIModelProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = "gpt-4o"
        self.embedding_model = "text-embedding-3-small"
        
    @property
    def model_name(self) -> str:
        return self.embedding_model
        
    async def generate(self, prompt: str, system_instruction: str) -> str:
        if not self.api_key:
            return self._mock_response(prompt, system_instruction)
            
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            return [[0.0] * 1536 for _ in texts]
            
        url = "https://api.openai.com/v1/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "text-embedding-3-small",
            "input": texts
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # OpenAI returns embeddings in the 'data' array
            # Sort by index just in case
            sorted_data = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_data]

    def _mock_response(self, prompt: str, system_instruction: str = "") -> str:
        # Check if this is a synthesizer request
        if "Synthesizer" in system_instruction:
            return f"""# CodeAtlas Expert Team Analysis (OpenAI)

## 🛡️ Security Perspective
I've reviewed the scope for `{prompt[:50]}...`. No major security vulnerabilities detected in the analyzed scope. The code handles inputs safely, but we should always ensure proper sanitization at the API boundaries.

## 🏗️ Architecture Perspective
The architecture follows a clean, decoupled design. The use of specialized layers (Controllers, Services, Repositories) makes it highly maintainable and scalable.

## ✨ Code Quality Perspective
The code adheres nicely to SOLID principles. The functions are concise and there is minimal technical debt.

### Conclusion
Overall, this section of the codebase is healthy and robust. If you'd like a deeper dive into a specific file, just ask!"""
            
        # Otherwise it's an expert agent request
        return "I have reviewed the codebase context. It looks well-structured and aligns with standard practices for my domain."
