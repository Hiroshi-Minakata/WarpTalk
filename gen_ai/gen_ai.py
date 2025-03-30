from abc import ABC, abstractmethod

class GenAI(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def chat(self, history: list[dict[str, str]] | None, prompt: str) -> str:
        """ History example is [{"role": "user", "prompt": "Hello"}, ...] """
        pass

    @abstractmethod
    def set_model(self, model_name: str, system_instruction: str = "You are an AI assistant.") -> bool:
        pass

    @abstractmethod
    def set_request_options(self, max_retry: int = 6, wait_time: float = 10) -> bool:
        pass