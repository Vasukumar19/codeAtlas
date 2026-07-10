from typing import Any


class ConversationManager:
    def __init__(self):
        self.history: list[dict[str, Any]] = []
        
    def add_turn(self, query: str, response: str):
        self.history.append({"query": query, "response": response})
