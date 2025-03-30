import regex as re

import config
from gen_ai.gen_ai import GenAI
from messenger.messenger import Event

class AI():


    def __init__(self, gen_ai: GenAI):
        self.__gen_ai = gen_ai

    def chat(self, event: Event, contexts: list[dict[str, str]]) -> list[str]:
        name = event.to.name
        timestamp = event.timestamp
        prompt = event.content.data

        # 生成
        system_instructions = f"あなたは{name}です。\n {config.SYSTEM_INSTRUCTIONS}"
        self.__gen_ai.set_model(config.MODEL_NAME, system_instructions)
        response = self.__gen_ai.chat(contexts, f"[{timestamp}] {prompt}")

        # 整形
        responses = format(response)
        return responses
    
    @staticmethod
    def format(text: str) -> list[str]:
        text = text.strip() # 前後の空白を削除
        text = re.sub(r"\[.*\]", "", text) # []とその中身を削除

        # 5文字以上の非空白文字の後に出現する記号を改行（末尾をのぞく）
        text = re.sub(r"(\S{5,})([!！?？])(?!$)", r"\1\2\n", text)

        # 5文字以上の非空白文字の後に出現する記号（"～"を除く）を改行（末尾をのぞく）
        text = re.sub(r"(\S{5,})(?!～)(\p{S})(?!$)", r"\1\2\n", text)
        
        texts = text.split("\n") # 改行ごとに分割
        return texts