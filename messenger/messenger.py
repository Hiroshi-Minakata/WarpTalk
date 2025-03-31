from enum import Enum
from dataclasses import asdict, dataclass, field
from abc import ABC, abstractmethod
from zoneinfo import ZoneInfo
from datetime import datetime
import json

from flask import Request

@dataclass
class Content:
    class Type(Enum):
        UNKNOWN = "UNKNOWN"
        TEXT = "TEXT"
        IMAGE = "IMAGE"
        VIDEO = "VIDEO"

    type: Type = Type.UNKNOWN
    data: str = ""

@dataclass
class User:
    id: str = ""
    name: str = ""

@dataclass
class To:
    id: str = ""
    name: str = ""
    users: list[User] = field(default_factory=list)

@dataclass
class Event:
    class Type(Enum):
        UNKNOWN = "UNKNOWN"
        MESSAGE = "MESSAGE"
        FOLLOW = "JOIN"
        UNFOLLOW = "LEAVE"
    type: Type = Type.UNKNOWN

    to: To = field(default_factory=To)
    sender: User = field(default_factory=User)
    content: Content = field(default_factory=Content)
    token: str = ""
    timestamp: str = field(init=False)

    ZONE: ZoneInfo = ZoneInfo("Asia/Tokyo")
    FORMAT: str = "%Y/%m/%d(%a) %H:%M"

    def __post_init__(self):
        self.timestamp = Event.get_timestamp()

    @staticmethod
    def get_timestamp() -> str:
        return datetime.now(Event.ZONE).strftime(Event.FORMAT)
    
    @staticmethod
    def is_timestamp(text: str) -> bool:
        try:
            datetime.strptime(text, Event.FORMAT)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def from_json(json_data: str) -> "Event":
        # JSON文字列を辞書に変換
        data = json.loads(json_data)

        # Eventオブジェクトを生成して返す
        event = Event()
        event.type = data["type"]

        event.to.id = data["to"]["id"]
        event.to.name = data["to"]["name"]
        event.to.users = [User(id=user['id'], name=user['name']) for user in data['to']['users']]

        event.sender.id = data["sender"]["id"]
        event.sender.name = data["sender"]["name"]

        event.content.type = data["content"]["type"]
        event.content.data = data["content"]["data"]

        event.token = data["token"]
        return event
    
    def to_json(self):
        return json.dumps(asdict(self), ensure_ascii=False, default=str)

class Messenger(ABC):
    @abstractmethod
    def verify(self, request: Request) -> bool:
        pass

    @abstractmethod
    def get(self, request: Request) -> list[Event]:
        pass

    @abstractmethod
    def send(self, events: list[Event]) -> bool:
        pass