from typing import override, List, Dict

from google import genai
from google.genai.types import Content, Part, Tool, GenerateContentConfig, GenerateContentResponse, GoogleSearch

from .gen_ai import GenAI

class Gemini(GenAI):
    def __init__(self, api_key: str):
        self.__client = genai.Client(api_key=api_key)
        self.model = "gemini-2.5-pro"
        self.system_instruction = ""
        self.__google_search_tool = Tool(google_search = GoogleSearch())

    def create_content(text: str, role: str) -> Content:
        """テキストとロールから、Contentオブジェクトを作成する"""
        return Content(parts=[Part(text=text)], role=role)
    
    def format_history(history: List[Dict[str, str]]) -> List[Content]:
        """辞書のリスト形式の履歴を、Contentオブジェクトのリストに変換する"""
        formatted_history: List[Content] = []
        for item in history:
            role = item.get("role")
            text = item.get("text")
            if role and text and role in ["model", "user"]:
                formatted_history.append(Gemini.create_content(text, role))
        return formatted_history

    @override
    def generate(self, prompt: str) -> str:
        """ 単一のプロンプトからテキストを生成 """
        contents = [Gemini.create_content(prompt, "user")]
        system_instruction_content = Gemini.create_content(self.system_instruction, "system")

        response: GenerateContentResponse = self.__client.models.generate_content(
            model=self.model,
            contents=contents,
            config=GenerateContentConfig(
                system_instruction=system_instruction_content,
                tools=[self.__google_search_tool],
                response_modalities=["TEXT"],
            ),
            )
        return response.text

    @override
    def chat(self, history: list[dict[str, str]] | None, prompt: str) -> str:
        """ 会話履歴に基づいてチャット """
        history.append({"role": "user", "text": prompt})
        
        # system指示を抽出
        system_texts = [item["text"] for item in history if item.get("role") == "system" and item.get("text")]
        system_instruction = "\n".join(system_texts + [self.system_instruction])
        system_instruction_content = Content(role="system", parts=[Part(text=system_instruction)])

        # system以外を会話履歴として使う
        conversation_history = [item for item in history if item.get("role") in ["user", "model"]]
        full_contents: List[Content] = Gemini.format_history(conversation_history)

        response: GenerateContentResponse = self.__client.models.generate_content(
            model=self.model,
            contents=full_contents,
            config=GenerateContentConfig(
                system_instruction=system_instruction_content,
                tools=[self.__google_search_tool],
                response_modalities=["TEXT"],
            ),
        )
        return response.text