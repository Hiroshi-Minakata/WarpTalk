from typing import override
import json

from flask import Request

import config
from .messenger import Messenger, Event, User

class DebugMessenger(Messenger):
    def __init__(self):
        self.message = ""

    @override
    def verify(self, request: Request) -> bool:
        return True

    @override
    def get(self, request: Request) -> list[Event]:
        messages: list[str] = json.loads(request.get_data(as_text=True))
        events: list[Event] = []

        for message in messages:
            event = Event()
            event.type = Event.Type.MESSAGE
            event.token = "Token"
            event.content.data = message

            # 送信先
            event.to.id = "0000"
            event.to.name = "Debuger"
            event.to.users.append(User("dummy1 ID", "dummy1 Name"))

            # 送信元
            event.sender.id = config.USER_ID
            event.sender.name = "Sender"

            events.append(event)

        return events

    @override
    def send(self, events: list[Event]) -> bool:
        json_data = [event.to_json() for event in events]
        datas = [Event.from_json(data) for data in json_data]
        print(datas)
        return True
    