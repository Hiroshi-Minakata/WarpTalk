import regex as re

import config
from gen_ai.gen_ai import GenAI
from messenger.messenger import Event

class AI():
    def __init__(self, gen_ai: GenAI):
        self.__gen_ai = gen_ai

    def init_profile(self, event: Event) -> list[str]:
        """ キャラクター設定 """
        self.__gen_ai.model = config.MODEL_NAME
        self.__gen_ai.system_instruction = ""

        # 生成
        instruction = config.GROUNDING1.replace("name", event.to.name)
        response = self.__gen_ai.generate(instruction)

        # 正規表現で先頭2行を削除
        response = re.sub(r'^(.*\n){2}', "", response)

        return ["", "system", response]

    def init_talk(self, event: Event, system_instruction: str) -> list[str]:
        """ キャラクターの会話を生成 """
        self.__gen_ai.model = config.MODEL_NAME
        self.__gen_ai.system_instruction = system_instruction

        # 生成
        instruction = config.GROUNDING2.replace("name", event.to.name)
        response = self.__gen_ai.generate(instruction)

        # 正規表現で先頭2行を削除
        response = re.sub(r'^(.*\n){2}', "", response)
        
        return ["", "system", response]

    def chat(self, event: Event, contexts: list[dict[str, str]] | None) -> list[str]:
        """ キャラクターになりきって会話 """
        name = event.to.name
        timestamp = event.timestamp
        prompt = event.content.data

        # 生成
        system_instructions = f"{name}として会話します。\n {config.SYSTEM_INSTRUCTIONS}"
        self.__gen_ai.model = config.MODEL_NAME
        self.__gen_ai.system_instruction = system_instructions
        response = self.__gen_ai.chat(contexts, f"[{timestamp}] {prompt}")

        # 整形
        responses = AI.format(response)
        return responses
    
    @staticmethod
    def format(text: str) -> list[str]:
        """ テキストを自然な形に整形と分割 """
        # []とその中身を削除
        text = re.sub(r"\[.*\]", "", text)

        # 5文字以上の非空白文字の後に出現する記号を改行
        # 二回連続の記号と末尾をのぞく
        text = re.sub(r"(\S{5,}?)([!！?？])(?![!！?？])(?!$)", r"\1\2\n", text)

        # 5文字以上の非空白文字の後に出現する記号を改行
        # "～"と"℃"と"℉"と"°"と末尾を除く
        text = re.sub(r"(\S{5,}?)(?!(?:～|℃|℉|°))(\p{S})(?!$)", r"\1\2\n", text)

        # 10文字以上の非空白文字の後に出現する"。"を改行
        # 末尾をのぞく
        text = re.sub(r"(\S{10,}?)([。])(?!$)", r"\1\2\n", text)

        # "..."を改行
        # 末尾をのぞく
        text = re.sub(r'(\.{3}?)(?!$)', r'\1\n', text)

        # 改行ごとに最大4分割し、前後の空白を削除
        texts = [line.strip() for line in text.split("\n", 4) if line.strip()]

        return texts