import asyncio

from app.intelligence.agents.expert import ExpertAgent
from app.intelligence.models.registry import ModelRegistry
from app.retrieval.domain.schemas import ContextPackage


class TeamOrchestrator:
    def __init__(self):
        self.experts = [
            ExpertAgent(
                "Security Expert",
                "Identifying vulnerabilities, injection risks, authentication flaws, and unsafe data handling."
            ),
            ExpertAgent(
                "Architecture Expert",
                "Analyzing software design patterns, decoupling, scalability, and structural bottlenecks."
            ),
            ExpertAgent(
                "Code Quality Expert",
                "Reviewing maintainability, technical debt, adherence to SOLID principles, and clean code practices."
            )
        ]

    async def orchestrate(self, query: str, context: ContextPackage, model_name: str = "OpenAI", strategy_focus: str = "") -> str:
        # Prepend focus to experts
        for expert in self.experts:
            expert.expertise = f"{strategy_focus}\n\n" + expert.expertise

        # 1. Run experts in parallel
        tasks = [
            expert.analyze(query, context, model_name)
            for expert in self.experts
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 2. Collect insights
        insights = ""
        for expert, result in zip(self.experts, results):
            if isinstance(result, Exception):
                insights += f"[{expert.role_name}]: Failed to analyze ({str(result)})\n\n"
            else:
                insights += f"[{expert.role_name}]:\n{result}\n\n"
                
        # 3. Synthesize
        provider = ModelRegistry.get(model_name)
        if not provider:
            raise ValueError(f"Provider {model_name} not found")
            
        system_instruction = f"""{strategy_focus}

You are the Lead Synthesizer for an AI Agent Team. 
You will receive a user query and the raw insights from your team of specialized experts (Security, Architecture, Quality).
Your job is to read all their insights, resolve any conflicting opinions, and produce a unified, comprehensive, and highly polished final response to the user.
Format the output in beautiful Markdown. Use headers, bullet points, and code blocks where appropriate.
Do not just list what the experts said; synthesize it into a cohesive narrative."""

        synthesis_prompt = f"User Query: {query}\n\n=== Expert Insights ===\n{insights}"
        
        final_response = await provider.generate(synthesis_prompt, system_instruction)
        return final_response
