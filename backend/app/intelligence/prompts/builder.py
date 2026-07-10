class PromptBuilder:
    def build(self, query: str, compressed_context: str) -> str:
        return f"User Query: {query}\n\nContext:\n{compressed_context}\n\nAnswer the query using ONLY the provided context."
