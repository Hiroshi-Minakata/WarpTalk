import logging

import config
from file_sys.file_sys import FileSys, Dir, File
from file_sys.spreadsheet import Spreadsheet
from messenger.messenger import Event

class DataManager():
    def __init__(self, user_data: FileSys, chat_data: FileSys):
        self.__user_data = user_data
        self.__chat_data = chat_data

    def regist_email(self, event: Event) -> str:
        # 保存先の確認
        user_id = event.sender.id
        user_name = event.sender.name

        user_file = self.__user_data.get_dir(config.USER_DATA_PATH).get_file(user_id)
        user_data: dict = user_file.read()
        url = user_data.get("url")

        if url:
            chat_dir: Spreadsheet = self.__chat_data.get_dir(url)
        else: # 保存先がない場合は作成
            chat_dir: Spreadsheet = self.__chat_data.create_dir(f"[WarpTalk]{user_name}")
            url = chat_dir.path
            user_file.write({"url": url})            

        # 共有先を設定
        email = event.content.data
        if not chat_dir.shere(email):
            url = ""
        return url
    
    def get_chat_data(self, event: Event) -> list[list]:
        chat_file = self.ensure_chat_data(event)
        return chat_file.read()
    
    def update_chat_data(self, event: Event, chat_data: list[list], reply_events: list[Event]) -> bool:
        # 初めて書き込む際の処理
        if not chat_data or not chat_data[0]:
            chat_data = []

        # ユーザーのメッセージ
        chat_data.append([event.timestamp, event.sender.name, event.content.data])

        # AIの返信を追加
        chat_data.extend([[r.timestamp, r.sender.name, r.content.data] for r in reply_events])

        # ファイルに書き込み
        chat_file = self.ensure_chat_data(event)
        return chat_file.write(chat_data)
    
    def ensure_chat_data(self, event: Event) -> File | None:
        user_id     = event.sender.id
        user_name   = event.sender.name

        # 保存先を取得
        user_file = self.__user_data.get_dir(config.USER_DATA_PATH).get_file(user_id)
        user_data: dict = user_file.read()

        if user_data:
            url = user_data.get("url")
            chat_dir: Dir = self.__chat_data.get_dir(url)
        else: # 保存先がない場合は作成
            chat_dir: Dir = self.__chat_data.create_dir(f"[WarpTalk]{user_name}")
            user_file.write({"url": chat_dir.path})    

        # ファイル
        chat_file = None
        group_id = event.to.id
        group_name = event.to.name
        if group_id and group_name:
            title = f"{group_name} - {group_id}"  

            # ファイルを取得（存在しない場合でもエラーを無視）
            logging.getLogger().setLevel(logging.CRITICAL)
            chat_file = chat_dir.get_file(title)
            logging.getLogger().setLevel(logging.NOTSET)

            # 存在しない場合は作成
            if chat_file is None:
                chat_file = chat_dir.create_file(title)
                
        return chat_file
    
    def delete_chat_data(self, event: Event) -> bool:
        id = event.sender.id
        user_file = self.__user_data.get_dir(config.USER_DATA_PATH).get_file(id)
        user_data: dict = user_file.read()

        # 削除済み
        if not (url := user_data.get("url")):
            return True

        # ファイル削除
        self.__chat_data.delete_dir(url)

        # 保存先削除
        user_file.write({"url":""})

        return True