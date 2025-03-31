from flask import Request

import config
from .format import Format
from messenger.messenger import Messenger, Event

class Chat():
    def __init__(self, messenger: Messenger):
        self.__messenger = messenger

    def get(self, request: Request) -> list[Event]:
        # 検証
        if not self.__messenger.verify(request):
            return []
        
        # 受信
        return self.__messenger.get(request)
    
    def send(self, events: list[Event]) -> bool:
        return self.__messenger.send(events)

    def set_email(self, event: Event) -> bool:
        reply_events = Format.strs_to_events([config.MESSAGE_SET_EMAIL], event)
        return self.__messenger.send(reply_events)
    
    def change_reply_time(self, event: Event) -> bool:
        reply_events = Format.strs_to_events([config.MESSAGE_REPLY_TIME], event)
        return self.__messenger.send(reply_events)
    
    def how_to_use(self, event: Event) -> bool:
        reply_events = Format.strs_to_events([config.MESSAGE_HOW_TO_USE], event)
        return self.__messenger.send(reply_events)
    
    def regist_email(self, event: Event, is_success: bool) -> bool:
        if is_success:
            reply_events = Format.strs_to_events([config.MESSAGE_OK_EMAIL], event)
        else:
            reply_events = Format.strs_to_events([config.MESSAGE_BAD_EMAIL], event)
        return self.__messenger.send(reply_events)