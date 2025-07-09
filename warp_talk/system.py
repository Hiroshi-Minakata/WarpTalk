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

    def __ensure_system_instructions(self, event: Event, chat_data: list[list]) -> bool:
        """ システム指示の確認 """
        is_success = True

        # プロフィールのシステム指示がない場合は1番目に追加
        if len(chat_data[0]) < 3 or chat_data[0][1] != "system" or not chat_data[0][2]:
            prompt = config.GROUNDING1.replace("name", event.to.name)
            chat_data[0] = self.__ai.gen_system_instruction(prompt)
            is_success &= self.__data_manager.write_chat_data(event, chat_data)

        # 自己紹介がない場合は2番目に追加
        if len(chat_data) < 2 or chat_data[1][1] != "system" or not chat_data[1][2]:
            prompt = config.GROUNDING2.replace("name", event.to.name)
            contexts = Format.chats_to_contexts([chat_data[0]], event)
            chat_data[1:2] = [self.__ai.gen_system_instruction(prompt, contexts)]
            is_success &= self.__data_manager.write_chat_data(event, chat_data)

        return is_success

    def execute(self, request: Request) -> bool:
        # 受信
        events = self.__chat.get(request)

        # イベントごとの処理
        is_success = True
        for event in events:
            if event.type is Event.Type.MESSAGE:
                is_success &= self.__send(event)
            elif event.type is Event.Type.FOLLOW:
                is_success &= self.__follow(event)
            elif event.type is Event.Type.UNFOLLOW:
                is_success &= self.__unfollow(event)
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
        # 会話履歴を取得
        chat_data:list[list] = self.__data_manager.get_chat_data(event)      

        # システム指示の確認
        contexts = Format.chats_to_contexts(chat_data, event)
        self.__ensure_system_instructions(event, chat_data)  
        responses = self.__ai.chat(event, contexts)
        reply_events: list[Event] = Format.strs_to_events(responses, event)

        # 会話履歴の更新
        self.__data_manager.update_chat_data(event, chat_data, reply_events)

        # 返信
        is_success = self.__chat.send(reply_events)
        return is_success

    def __official(self, event: Event) -> bool:
        message = event.content.data

        if message == config.SYSTEM_SET_EMAIL: # アカウントを設定
            return self.__chat.set_email(event)
        elif message == config.SYSTEM_REPLY_TIME: # 返信時期を変更
            return self.__chat.change_reply_time(event)
        elif message == config.SYSTEM_HOW_TO_USE: # 使い方
            return True
        else: # アカウントの登録
            url = self.__data_manager.regist_email(event)
            return self.__chat.regist_email(event, url)
        
    def __follow(self, event: Event) -> bool:
        self.__data_manager.ensure_chat_data(event)
        return True
        
    def __unfollow(self, event: Event) -> bool:
        return self.__data_manager.delete_chat_data(event)
    
    def __join(self, event: Event) -> bool:
        print(event.to.id, event.to.name, event.sender.id, event.sender.name)
        return True
    
    def __leave(self, event: Event) -> bool:
        print(event.to.id, event.to.name, event.sender.id, event.sender.name)
        return True