from typing import Any, override
import logging

from google.api_core import retry
import google.generativeai as genai
from google.generativeai.types import RequestOptions

from .gen_ai import GenAI

class Gemini(GenAI):
    def __init__(self, api_key: str):
        # 認証
        genai.configure(api_key=api_key)

        # 設定
        self.__model = self.set_model()
        self.__request_options = self.set_request_options()

    @override
    def generate(self, prompt: str) -> str:
        response = self.__model.generate_content(prompt, request_options=self.__request_options)
        return response.text

    @override
    def chat(self, history: list[dict[str, Any]], prompt: str) -> str:
        chat = self.__model.start_chat(history=history)
        response = chat.send_message(
            prompt,
            request_options=self.__request_options
        )
        return response.text

    @override
    def set_model(self, model_name: str = "gemini-1.5-pro", system_instruction: str = "You are an AI assistant.") -> bool:
        try:
            self.__model = genai.GenerativeModel(model_name, system_instruction=system_instruction)
            return True
        except Exception as e:
            logging.exception(e)
            return False

    @override
    def set_request_options(self, max_retry: int = 6, wait_time: float = 10) -> bool:
        try:
            max_wait_time = wait_time * max_retry
            self.__request_options = RequestOptions(
                retry=retry.Retry(
                    initial=wait_time,
                    multiplier=1,
                    maximum=max_wait_time,
                    timeout=max_wait_time
                ))
            return True
        except Exception as e:
            logging.exception(e)
            return False