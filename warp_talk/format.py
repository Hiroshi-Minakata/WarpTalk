from messenger.messenger import Event, Content

class Format():
    @staticmethod
    def chats_to_contexts(chats: list[list[str, str, str]], event: Event) -> list[dict[str, str]]:
        """ リストを辞書に変換 """
        contexts: list[dict[str, str]] = []
        for chat in chats:
            # 要素が3つ以上あるか確認
            if len(chat) < 3:
                continue

            # データを要素ごとに分割
            timestamp, name, message = (chat + [None] * 3)[:3]

            # タイムスタンプの確認
            if not Event.is_timestamp(timestamp):
                continue

            # ロールの設定
            role = "model" if name == event.to.name else "user"

            # 会話履歴の追加
            contexts.append({"role": role, "text": f"[{timestamp}] {message}"})

        return contexts
    
    @staticmethod
    def strs_to_events(messages: list[str], event: Event) -> list[Event]:
        """ 文字列をEventに変換 """
        events: list[Event] = []
        for message in messages:
            new_event = Event()
            new_event.token = event.token
            new_event.to.id = event.to.id
            new_event.sender.name = event.to.name
            new_event.content = Content(Content.Type.TEXT, message)
            events.append(new_event)

        return events