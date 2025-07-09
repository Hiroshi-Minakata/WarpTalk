import time
import random
from abc import ABC, abstractmethod

class GenAI(ABC):
    def __init__(self):
        self.model = ""
        self.system_instruction = ""
        self.max_retries = 6

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

    @abstractmethod
    def chat(self, history: list[dict[str, str]] | None, prompt: str) -> str:
        """ History example is [{"role": "user", "text": "Hello"}, ...] """
        pass

    def _call_with_retry(self, func, *args, **kwargs):
        """指数バックオフでリトライを実行"""
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries:
                    raise e
                
                # 指数バックオフ（ジッターあり）
                delay = (2 ** attempt) + random.uniform(0, 1)
                print(f"リトライ {attempt + 1}/{self.max_retries} - {delay:.2f}秒後に再試行")
                time.sleep(delay)