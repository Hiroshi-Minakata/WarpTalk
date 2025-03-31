import logging

import config
from file_sys.file_sys import FileSys, Dir
from file_sys.spreadsheet import Spreadsheet
from messenger.messenger import Event

class DataManager():
    def __init__(self, user_data: FileSys, chat_data: FileSys):
        self.__user_data = user_data
        self.__chat_data = chat_data

    def regist_email(self, event: Event) -> bool:
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
            user_file.write({"url": chat_dir.path})            

        # 共有先を設定
        email = event.content.data
        return chat_dir.shere(email)
    
    def get_chat_data(self, event: Event) -> list[list]:
        user_id = event.sender.id
        user_name = event.sender.name
        group_id = event.to.id
        group_name = event.to.name
        title = f"{group_name} - {group_id}"

        # 保存先を取得
        user_file = self.__user_data.get_dir(config.USER_DATA_PATH).get_file(user_id)
        user_data: dict = user_file.read()
        url = user_data.get("url")

        if url:
            chat_dir: Dir = self.__chat_data.get_dir(url)
        else: # 保存先がない場合は作成
            chat_dir: Dir = self.__chat_data.create_dir(f"[WarpTalk]{user_name}")
            user_file.write({"url": chat_dir.path})      

        # ファイルを取得（存在しない場合でもエラーを無視）
        logging.getLogger().setLevel(logging.CRITICAL)
        chat_file = chat_dir.get_file(title)
        logging.getLogger().setLevel(logging.NOTSET)
        
        # 存在しない場合は作成
        if chat_file is None:
            chat_file = chat_dir.create_file(title)

        return chat_file.read()
    
    def update_chat_data(self, event: Event, chat_data: list[list], reply_events: list[Event]) -> bool:
        # 初めて書き込む際の処理
        if not chat_data or not chat_data[0]:
            chat_data = []

        # ユーザーのメッセージ
        chat_data.append([event.timestamp, event.sender.name, event.content.data])

        # AIの返信を追加
        chat_data.extend([[r.timestamp, r.sender.name, r.content.data] for r in reply_events])

        user_id = event.sender.id
        group_id = event.to.id
        group_name = event.to.name

        # 保存先を取得
        user_file = self.__user_data.get_dir(config.USER_DATA_PATH).get_file(user_id)
        user_data: dict = user_file.read()
        chat_dir = self.__chat_data.get_dir(user_data.get("url"))
        title = f"{group_name} - {group_id}"
        chat_file = chat_dir.get_file(title)

        # 存在しない場合は作成
        if chat_file is None:
            chat_file = chat_dir.create_file(title)
        
        return chat_file.write(chat_data)
    
    def delete_chat_data(self, event: Event) -> bool:
        id = event.sender.id
        data: dict = self.__user_data.get_dir(config.USER_DATA_PATH).get_file(id).read()
        self.__chat_data.delete_dir(data.get("url"))