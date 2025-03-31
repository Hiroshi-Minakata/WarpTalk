from flask import Flask, request

import config
from file_sys.firebase import Firebase
from file_sys.spreadsheet import GSpread
from gen_ai.gemini import Gemini
from messenger.line import Line
from warp_talk.system import System

app = Flask(__name__)

# 開発環境ごとに認証情報を取得
cert = "key.json" if config.ENV == "DEV" else None

# インスタンスの初期化
user_db     = Firebase(cert)
chat_db     = GSpread(cert)
gen_ai      = Gemini(config.API_KEY)
messenger   = Line(config.CHANNEL_ACCESS_TOKEN, config.CHANNEL_SECRET)
system      = System(user_db, chat_db, gen_ai, messenger)

# エントリポイント
@app.route("/", methods=["POST"])
def entry_point():
    is_success = system.execute(request)
    return ("OK", 200) if is_success else ("BAD", 400)
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT)