from typing import List, Dict, Any

class ConversationManager:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []
        
    def add_turn(self, query: str, response: str):
        self.history.append({"query": query, "response": response})
