class PromptBuilder:
    def build(self, query: str, compressed_context: str, history: list[dict] = None) -> str:
        history_str = ""
        if history:
            history_str = "Conversation History:\n"
            for turn in history[-10:]:
                history_str += f"User: {turn['query']}\nAssistant: {turn['response']}\n\n"
        return f"{history_str}User Query: {query}\n\nContext:\n{compressed_context}\n\nAnswer the query using ONLY the provided context."
