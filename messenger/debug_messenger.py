from typing import override
import json

from flask import Request

from .messenger import Messenger, Event, User

class DebugMessenger(Messenger):
    def __init__(self):
        self.message = ""

    @override
    def verify(self, request: Request) -> bool:
        return True

    @override
    def get(self, request: Request) -> list[Event]:
        with open("debug/request.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        messages: list[str] = data["messages"]
        events: list[Event] = []

        for message in messages:
            event = Event()
            event.type = Event.Type(data["event_type"])
            event.token = data["token"]
            event.content.data = message

            # 送信先
            event.to.id = data["to_id"]
            event.to.name = data["to_name"]
            event.to.users.append(User("dummy1 ID", "dummy1 Name"))

            # 送信元
            event.sender.id = data["sender_id"]
            event.sender.name = data["sender_name"]

            events.append(event)

        return events

    @override
    def send(self, events: list[Event]) -> bool:
        json_data = [event.to_json() for event in events]
        datas = [Event.from_json(data) for data in json_data]
        print(datas)
        return True
    