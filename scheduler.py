import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from linebot import LineBotApi
from linebot.models import TextSendMessage

# mentionクラス有無で自動フォールバック
try:
    from linebot.models import Mention, Mentionee
    USE_OBJ = True
except Exception:
    USE_OBJ = False

load_dotenv()
TOKEN  = os.getenv("CHANNEL_ACCESS_TOKEN")
GROUP  = os.getenv("GROUP_ID_MAIN")        # 既存メイングループ
GROUP2 = os.getenv("GROUP_ID_SECOND")      # 新チャネル（必須）
KAZUO  = os.getenv("USER_ID_KAZUO")
YUKIKO = os.getenv("USER_ID_YUKIKO")
assert all([TOKEN, GROUP, GROUP2, KAZUO, YUKIKO]), ".env を埋めてください"

bot = LineBotApi(TOKEN)

# 既存メイングループ向け
def send(text, mentionees=None):
    if mentionees:
        if USE_OBJ:
            ments = []
            for m in mentionees:
                if m["type"] == "all":
                    ments.append(Mentionee(type="all", index=m["index"], length=m["length"]))
                else:
                    ments.append(Mentionee(type="user", user_id=m["userId"], index=m["index"], length=m["length"]))
            msg = TextSendMessage(text=text, mention=Mention(mentionees=ments))
        else:
            msg = TextSendMessage(text=text, mention={"mentionees": mentionees})
    else:
        msg = TextSendMessage(text=text)
    bot.push_message(GROUP, msg)

# 任意グループ向け（GROUP2 でも使う）— Mention/Mentionee対応
def send_to(group_id, text, mentionees=None):
    if mentionees:
        if USE_OBJ:
            ments = []
            for m in mentionees:
                if m["type"] == "all":
                    ments.append(Mentionee(type="all", index=m["index"], length=m["length"]))
                else:
                    ments.append(Mentionee(type="user", user_id=m["userId"], index=m["index"], length=m["length"]))
            msg = TextSendMessage(text=text, mention=Mention(mentionees=ments))
        else:
            msg = TextSendMessage(text=text, mention={"mentionees": mentionees})
    else:
        msg = TextSendMessage(text=text)
    bot.push_message(group_id, msg)

# ── 毎日（既存） ─────────────────────
def d_0600():
    at = "@石橋和大"
    txt = f"{at}\n日本の朝6時です、P活ルーティンをせよ。"
    send(txt, [{"type":"user","userId":KAZUO,"index":0,"length":len(at)}])

def d_1200():
    at="@all"; txt=f"{at}\n昼12時、昼のWEB講演会あるかもよ。"
    send(txt, [{"type":"all","index":0,"length":len(at)}])

def d_1800():
    at="@all"; txt=f"{at}\n夕18時、WEB講演会大丈夫かい。"
    send(txt, [{"type":"all","index":0,"length":len(at)}])

def d_2100():
    at_all="@all"; at_y="@石橋夕稀子"
    txt=(f"{at_all}\n夜21時、夜のルーティンね。\n"
         f"{at_y}\nいつものアンケート案件よろしく。\n（m3, プラメド、 Medure、日経、care）")
    send(txt, [
        {"type":"all","index":0,"length":len(at_all)},
        {"type":"user","userId":YUKIKO,"index":txt.find(at_y),"length":len(at_y)}
    ])

# ── 毎週・毎月（既存） ────────────────
def w_sat_1500():
    at="@石橋夕稀子"
    txt=(f"{at}\nプラメドの締め切りが近いです。よろしくお願いいたします。\n"
        "https://docs.google.com/spreadsheets/d/1qdYP3TIUQIyzYyYukpvtrF3EsBT2uM8gDtxiTgpCMkY/edit?gid=1676746958#gid=1676746958")
    send(txt, [{"type":"user","userId":YUKIKO,"index":0,"length":len(at)}])

def m_28_0900():
    at="@石橋夕稀子"
    txt=(f"{at}\nm3の締め切りが近いです。よろしくお願いいたします。\n"
        "https://docs.google.com/spreadsheets/d/1qdYP3TIUQIyzYyYukpvtrF3EsBT2uM8gDtxiTgpCMkY/edit?gid=1676746958#gid=1676746958")
    send(txt, [{"type":"user","userId":YUKIKO,"index":0,"length":len(at)}])

def m_02_0900():
    at="@石橋夕稀子"
    txt=(f"{at}\nIQVIAの締め切りが近いです。よろしくお願いいたします。\n"
        "https://docs.google.com/spreadsheets/d/1qdYP3TIUQIyzYyYukpvtrF3EsBT2uM8gDtxiTgpCMkY/edit?gid=1676746958#gid=1676746958")
    send(txt, [{"type":"user","userId":YUKIKO,"index":0,"length":len(at)}])

# ── GROUP2 用 ────────────────────────
def d_0700_group2():
    at = "@all"
    txt = (f"{at}\n毎朝7時。\n"
           "朝活してますか？日光浴びてますか？深呼吸できてますか？\n"
           "セコムしてますか？")
    send_to(GROUP2, txt, [{"type":"all","index":0,"length":len(at)}])

def d_2200_group2():
    at_all = "@all"
    at_k   = "@石橋和大"
    txt = (f"{at_all}\n毎晩22時。\n"
           f"{at_k}\nそろそろ閉業の準備ね。23時までには\n"
           "ストレッチ、片付け、明日準備、必ずね。\n"
           "今日もお疲れ様でした。")
    send_to(GROUP2, txt, [
        {"type":"all","index":0,"length":len(at_all)},
        {"type":"user","userId":KAZUO,"index":txt.find(at_k),"length":len(at_k)}
    ])

def main():
    tz = "Asia/Tokyo"
    sch = BackgroundScheduler(timezone="Asia/Tokyo")
    # 既存
    sch.add_job(d_0600, CronTrigger(hour=6))
    sch.add_job(d_1200, CronTrigger(hour=12))
    sch.add_job(d_1800, CronTrigger(hour=18))
    sch.add_job(d_2100, CronTrigger(hour=21))
    sch.add_job(w_sat_1500, CronTrigger(day_of_week="sat", hour=15))
    sch.add_job(m_28_0900, CronTrigger(day="28", hour=9))
    sch.add_job(m_02_0900, CronTrigger(day="2",  hour=9))
    # GROUP2
    sch.add_job(d_0700_group2, CronTrigger(hour=7))
    sch.add_job(d_2200_group2, CronTrigger(hour=22))
    print("Scheduler started (JST)")
    sch.start()

if __name__ == "__main__":
    main()


