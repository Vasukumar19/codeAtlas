from typing import Optional
from app.intelligence.models.registry import ModelRegistry
from app.retrieval.domain.schemas import ContextPackage

class ExpertAgent:
    def __init__(self, role_name: str, expertise: str):
        self.role_name = role_name
        self.expertise = expertise
        
    async def analyze(self, query: str, context: ContextPackage, model_name: str = "Gemini") -> str:
        provider = ModelRegistry.get(model_name)
        if not provider:
            raise ValueError(f"Provider {model_name} not found")
            
        system_instruction = f"""You are a {self.role_name}. Your expertise is: {self.expertise}.
Your task is to analyze the user's query and the provided codebase context exclusively through the lens of your expertise.
Do not provide a general answer. Provide specific, deep insights related to your domain.
If the context is irrelevant to your expertise, state that clearly."""

        # Format context loosely for the expert
        context_str = f"Query: {query}\n\n"
        if context.primary_nodes:
            context_str += "Relevant Code Files & Symbols:\n"
            for node in context.primary_nodes:
                context_str += f"- {node.path} ({node.type}):\n{node.content}\n\n"
        
        response = await provider.generate(context_str, system_instruction)
        return response
