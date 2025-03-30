from flask import Request

import config
from file_sys.file_sys import FileSys
from gen_ai.gen_ai import GenAI
from messenger.messenger import Messenger, Event
from .ai import AI
from .chat import Chat
from .data_manager import DataManager
from .format import Format

class System():
    def __init__(self, user_data: FileSys, chat_data: FileSys, gen_ai: GenAI, messenger: Messenger):
        self.__data_manager = DataManager(user_data, chat_data)
        self.__ai = AI(gen_ai)
        self.__chat = Chat(messenger)

    def execute(self, request: Request) -> bool:
        # 受信
        events = self.__chat.get(request)

        # イベントごとの処理
        is_success = True
        for event in events:
            if event.type is Event.Type.MESSAGE:
                is_success &= self.__send(event)
            elif event.type is Event.Type.JOIN:
                is_success &= self.__join(event)
            elif event.type is Event.Type.LEAVE:
                is_success &= self.__leave(event)

        return is_success
    
    def __send(self, event: Event) -> bool:
        # 送信先を選択
        if event.to.users:
            return self.__group(event)
        else:
            return self.__official(event)
        
    def __group(self, event: Event) -> bool:
        # コンテキストを生成
        chat_data = self.__data_manager.get_chat_data(event)
        contexts = Format.chats_to_contexts(chat_data, event)

        # AIによる返答の構築
        responses = self.__ai.chat(event, contexts)
        reply_events: list[Event] = Format.strs_to_events(responses, event)

        # 会話履歴の更新
        self.__data_manager.update_chat_data(event, chat_data, reply_events)

        # 返信
        is_success = self.__chat.send(reply_events)
        return is_success

    def __official(self, event: Event) -> bool:
        message = event.content.data

        if message == config.SYSTEM_SET_URL: # 保存先の設定
            return self.__chat.set_url(event)
        elif message == config.SYSTEM_REPLY_TIME: # 返信時期を変更
            return self.__chat.change_reply_time(event)
        elif message == config.SYSTEM_HOW_TO_USE: # 使い方
            return self.__chat.how_to_use(event)
        else: # 保存先を登録
            is_success = self.__data_manager.regist_url(event)
            return self.__chat.regist_url(event, is_success)
        
    def __join(self, event: Event) -> bool:
        return True
        
    def __leave(self, event: Event) -> bool:
        return True