from typing import override
import logging

from flask import Request
from linebot import LineBotApi
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi
from linebot.v3.webhooks.models import MessageEvent, FollowEvent, UnfollowEvent, TextMessageContent, GroupSource
from linebot.v3.messaging.models import TextMessage, ImageMessage, VideoMessage, ReplyMessageRequest, PushMessageRequest

from .messenger import Messenger, Event, Content, User

class Line(Messenger):
    def __init__(self, channel_access_token: str, channel_secret: str):
        # 認証
        config = Configuration(access_token=channel_access_token)
        client = ApiClient(config)
        self.__line_bot_api = LineBotApi(channel_access_token)
        self.__handler = WebhookHandler(channel_secret)
        self.__messaging_api = MessagingApi(client)

    @override
    def verify(self, request: Request) -> bool:
        # ヘッダ
        if (signature := request.headers.get("X-Line-Signature")) is None:
            logging.error("Signature is None.")
            return False
        
        # ボディ
        if (body := request.get_data(as_text=True)) is None:
            logging.error("Body is None.")
            return False
        
        # 署名の検証
        try: 
            self.__handler.parser.parse(body, signature)
            return True
        except InvalidSignatureError:
            logging.error("Invalid signature.")
            return False

    @override
    def get(self, request: Request) -> list[Event]:
        signature = request.headers.get("X-Line-Signature")
        body = request.get_data(as_text=True)
        payload = self.__handler.parser.parse(body, signature, as_payload=True)
        events: list[Event] = []

        for line_event in payload.events:
            event = Event()

            # イベントごとに処理
            if isinstance(line_event, MessageEvent): # 受信
                event.type = Event.Type.MESSAGE
                event.token = line_event.reply_token

                # コンテンツごとに処理
                if isinstance(line_event.message, TextMessageContent):
                    data = line_event.message.text
                    event.content = Content(Content.Type.TEXT, data)
            elif isinstance(line_event, FollowEvent): # グループ参加
                event.type = Event.Type.FOLLOW
                event.token = line_event.reply_token
            elif isinstance(line_event, UnfollowEvent): # グループ退会
                event.type = Event.Type.UNFOLLOW
            else: # 不明イベント
                event.type = Event.Type.UNKNOWN

            # 送信先
            source = line_event.source
            if isinstance(source, GroupSource): # ユーザーからグループへ
                event.to.id = source.group_id
                try:
                    group_summary = self.__line_bot_api.get_group_summary(source.group_id)
                    event.to.name = group_summary.group_name
                except Exception as e:
                    logging.exception(e)
                    event.to.name = None

                # Members
                # https://developers.line.biz/en/reference/messaging-api/#get-group-member-user-ids
                # "この機能は認証済みアカウントまたはプレミアムアカウントでのみご利用いただけます。"
                # group_member_ids = self.__line_bot_api.get_group_member_ids(source.group_id)
                # for id in group_member_ids.member_ids:
                #    profile = self.__line_bot_api.get_profile(source.user_id)
                #    event.to.members.append(Member(id, profile.display_name))
                event.to.users.append(User("dummy", "dummy"))
            else: # ユーザーから公式へ
                bot_info = self.__line_bot_api.get_bot_info()
                event.to.id = bot_info.user_id
                event.to.name = bot_info.display_name

            # 送信元のユーザー
            event.sender.id = source.user_id
            try:
                profile = self.__line_bot_api.get_profile(source.user_id)
                event.sender.name = profile.display_name
            except Exception as e:
                logging.exception(e)
                event.sender.name = None

            # Add
            events.append(event)

        return events

    @override
    def send(self, events: list[Event]) -> bool:
        messages = []
        for event in events:
            # コンテンツごとに処理
            if event.content.type is Content.Type.TEXT:
                messages.append(TextMessage(text=event.content.data))
            elif event.content.type is Content.Type.IMAGE:
                url = event.content.data
                messages.append(ImageMessage(originalContentUrl=url, previewImageUrl=url))
            elif event.content.type is Content.Type.VIDEO:
                url = event.content.data
                messages.append(VideoMessage(originalContentUrl=url, previewImageUrl=url))

        # ReplyMessageはFreeプランで制限なし
        # 1つのトークンに対して、まとめて返信（5通まで）
        # 応答トークンは1分以内まで保証
        try:
            request = ReplyMessageRequest(replyToken=event.token, messages=messages)
            self.__messaging_api.reply_message(request)
        except Exception:
            # PushMessageはFreeプランで200件/月まで
            # 期限切れの場合はプッシュメッセージで送信
            try:
                request = PushMessageRequest(to=event.to.id, messages=messages)
                self.__messaging_api.push_message(request)
            except Exception as e:
                logging.exception(e)
                return False
            
        return True