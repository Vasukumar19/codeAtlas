import json

from app.intelligence.domain.schemas import StructuredAIResponse


class ResponseFormatter:
    def format(self, raw_response: str) -> StructuredAIResponse:
        data = json.loads(raw_response)
        return StructuredAIResponse(**data)
