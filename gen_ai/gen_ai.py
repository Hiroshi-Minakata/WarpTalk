from abc import ABC, abstractmethod

class GenAI(ABC):
    def __init__(self, model: str, system_instruction: str):
        self.model = model
        self.system_instruction = system_instruction

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def chat(self, history: list[dict[str, str]] | None, prompt: str) -> str:
        """ History example is [{"role": "user", "text": "Hello"}, ...] """
        pass