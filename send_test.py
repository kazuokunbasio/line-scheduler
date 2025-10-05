import os
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

load_dotenv()
TOKEN  = os.getenv("CHANNEL_ACCESS_TOKEN")
GROUP3 = os.getenv("GROUP_ID_THIRD")

assert TOKEN and GROUP3, ".env に CHANNEL_ACCESS_TOKEN / GROUP_ID_THIRD を設定してください"

bot = LineBotApi(TOKEN)

def simple_comment():
    text = "石橋さんおもろっ"
    msg = TextSendMessage(text=text)
    bot.push_message(GROUP3, msg)
    print("💬 コメント送信しました。")

if __name__ == "__main__":
    simple_comment()
