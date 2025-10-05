import os
from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, JoinEvent, TextSendMessage
from scheduler import start_scheduler

load_dotenv()
app = Flask(__name__)
start_scheduler()   # Gunicorn -w 1 なので二重起動しません
SECRET = os.getenv("CHANNEL_SECRET")
TOKEN  = os.getenv("CHANNEL_ACCESS_TOKEN")
api = LineBotApi(TOKEN)
handler = WebhookHandler(SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    sig = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try: handler.handle(body, sig)
    except InvalidSignatureError: abort(400)
    return "OK"

@handler.add(JoinEvent)
def on_join(e):
    gid = e.source.group_id
    print(f"[JOIN] GROUP_ID={gid}", flush=True)
    api.reply_message(e.reply_token, TextSendMessage(text=f"グループID取得OK:\n{gid}"))

@handler.add(MessageEvent, message=TextMessage)
def on_msg(e):
    gid = getattr(e.source, "group_id", None)
    uid = e.source.user_id
    name = None
    try:
        prof = api.get_group_member_profile(gid, uid) if gid else api.get_profile(uid)
        name = prof.display_name
    except Exception: pass
    print(f"[MSG] USER_ID={uid} NAME={name} GROUP_ID={gid}", flush=True)
    if e.message.text.strip().lower() == "id":
        api.reply_message(e.reply_token, TextSendMessage(text=f"USER_ID={uid}\nNAME={name}\nGROUP_ID={gid}"))

@app.route("/ping", methods=["GET", "HEAD"])
def ping():
    return ("", 204)



@app.get("/")
def health():
    return "alive", 200

if __name__ == "__main__":
    app.run("0.0.0.0", 8000)





