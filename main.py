from flask import Flask, request

import config
from file_sys.firebase import Firebase
from file_sys.spreadsheet import GSpread
from gen_ai.gemini import Gemini
from messenger.line import Line
from messenger.debug_messenger import DebugMessenger
from warp_talk.system import System

app = Flask(__name__)

# インスタンス
user_db = None
chat_db = None
gen_ai = None
messenger = None

def factory() -> System:
    global user_db, chat_db, gen_ai, messenger

    # DB各種
    if user_db is not Firebase:
        cert = "debug/key.json" if config.ENV == "DEV" else None
        user_db = Firebase(cert)

    # DB各種
    if chat_db is not GSpread:
        cert = "debug/key.json" if config.ENV == "DEV" else None
        chat_db = GSpread(cert)

    # AI各種
    if gen_ai is not Gemini:
        gen_ai = Gemini(config.API_KEY)

    # メッセンジャー各種
    messenger_app = request.args.get("messenger_app")
    if messenger_app == "Line" and messenger is not Line:
        messenger = Line(config.CHANNEL_ACCESS_TOKEN, config.CHANNEL_SECRET)
    else:
        messenger = DebugMessenger()

    return System(user_db, chat_db, gen_ai, messenger)

# エントリポイント
@app.route("/", methods=["POST"])
def entry_point():
    system = factory()
    is_success = system.execute(request)    
    return ("OK", 200) if is_success else ("BAD", 400)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT)