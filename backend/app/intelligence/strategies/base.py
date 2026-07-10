from abc import ABC, abstractmethod

class ReasoningStrategy(ABC):
    @abstractmethod
    def build_system_instruction(self) -> str:
        pass
