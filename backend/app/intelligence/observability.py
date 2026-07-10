import time

class Observability:
    @staticmethod
    def log(model: str, prompt_size: int, latency_ms: int):
        # Mock logging
        print(f"Model: {model}, Prompt Size: {prompt_size}, Latency: {latency_ms}ms")
