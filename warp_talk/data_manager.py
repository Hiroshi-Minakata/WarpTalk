import logging

import config
from file_sys.file_sys import FileSys, File
from messenger.messenger import Event

class DataManager():
    def __init__(self, user_data: FileSys, chat_data: FileSys):
        self.__user_data = user_data
        self.__chat_data = chat_data
        pass

    def regist_url(self, event: Event) -> bool:
        # 保存先の存在確認
        chat_data_path = event.content.data
        directory = self.__chat_data.get_dir(chat_data_path)
        if directory is None:
            return False

        # 保存先を登録
        return self.get_user_data(event.sender.id).write({"chat_data_path": chat_data_path})

    def get_user_data(self, file_name: str) -> File | None:
        directory = self.__user_data.get_dir(config.USER_DATA_PATH)
        return directory.get_file(file_name)
    
    def get_chat_data_file(self, event: Event) -> File | None:
        # 保存先を取得
        if (user_data_file := self.get_user_data(event.sender.id)) is None:
            return None
        
        # パスを取得
        user_data: dict | None = user_data_file.read()        
        chat_data_path: str | None = user_data.get("chat_data_path")
        if chat_data_path is None:
            return None
        
        # ファイルを取得
        chat_data_file = self.ensure_chat_data(event, chat_data_path)
        return chat_data_file
    
    def get_chat_data(self, event: Event) -> list[list]:
        """ 会話履歴を取得 """
        if (chat_data_file := self.get_chat_data_file(event)) is None:
            return [[]]
        if (chat_data := chat_data_file.read()) is None:
            return [[]]
        return chat_data
    
    def update_chat_data(self, event: Event, chat_data: list[list], reply_events: list[Event]) -> bool:
        # 初めて書き込む際の処理
        if not chat_data or not chat_data[0]:
            chat_data = []

        # ユーザーのメッセージ
        chat_data.append([event.timestamp, event.sender.name, event.content.data])

        # AIの返信を追加
        for replay in reply_events:
            chat_data.append([replay.timestamp, replay.sender.name, replay.content.data])

        # 会話履歴の保存
        if (chat_data_file := self.get_chat_data_file(event)) is None:
            return False
        if chat_data_file.write(chat_data) is False:
            return False
        
        return True
    
    def ensure_chat_data(self, event: Event, chat_data_path: str) -> File:        
        # ディレクトリを取得
        dir = self.__chat_data.get_dir(chat_data_path)
        file_name = f"{event.to.name} - {event.to.id}"
        
        # ファイルを取得（存在しない場合でもエラーを無視）
        logging.getLogger().setLevel(logging.CRITICAL)
        file = dir.get_file(file_name)
        logging.getLogger().setLevel(logging.NOTSET)

        # 存在しない場合は再生成
        if file is None:
            file = dir.create_file(file_name)        

        return file