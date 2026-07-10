from abc import ABC, abstractmethod


class ReasoningStrategy(ABC):
    def build_system_instruction(self) -> str:
        base = (
            "You are CodeAtlas, an expert software intelligence engine. "
            "You MUST output your response as a valid JSON object matching this schema:\n"
            "{\n"
            "  \"type\": \"string (e.g. Architecture Explanation, Bug Investigation)\",\n"
            "  \"title\": \"string\",\n"
            "  \"summary\": \"string\",\n"
            "  \"sections\": [{\"title\": \"string\", \"content\": \"string\"}],\n"
            "  \"steps\": [\"string (for execution flows or debug steps)\"],\n"
            "  \"citations\": [{\"node_id\": \"uuid string found in context\", \"confidence\": 0.9}],\n"
            "  \"confidence\": 0.95,\n"
            "  \"metadata\": {}\n"
            "}\n"
            "Do not include markdown blocks like ```json around the output. Only return raw JSON. "
            "Use the provided context to answer. When citing context, include the exact UUID in citations."
        )
        return base + "\n\n" + self.get_specific_instructions()
        
    @property
    @abstractmethod
    def response_type(self) -> str:
        """The type string to return in the JSON response."""
        pass

    @property
    @abstractmethod
    def response_title(self) -> str:
        """The title string to return in the JSON response."""
        pass
        
    @property
    def requires_team(self) -> bool:
        """Whether this strategy requires the Multi-Agent team execution."""
        return False
        
    @abstractmethod
    def get_specific_instructions(self) -> str:
        pass
