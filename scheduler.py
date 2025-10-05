# scheduler.py
import os
import time
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from linebot import LineBotApi
from linebot.models import TextSendMessage

# Mention クラスがある SDK / ない SDK の両対応
try:
    from linebot.models import Mention, Mentionee
    USE_OBJ = True
except Exception:
    USE_OBJ = False

# --- グローバル（遅延初期化） ---
SCHED = None
BOT = None
GROUP = ""
GROUP2 = ""
KAZUO = ""
YUKIKO = ""
_STARTED = False  # 二重起動防止フラグ


# ============= 送信ユーティリティ =============
def _ensure_bot_initialized():
    if BOT is None:
        raise RuntimeError("BOT is not initialized. Call start_scheduler() first.")

def send(text, mentionees=None):
    """既存メイングループへ送信"""
    _ensure_bot_initialized()
    if mentionees:
        if USE_OBJ:
            ments = [
                (Mentionee(type="all", index=m["index"], length=m["length"])
                 if m.get("type") == "all"
                 else Mentionee(type="user", user_id=m["userId"],
                                index=m["index"], length=m["length"]))
                for m in mentionees
            ]
            msg = TextSendMessage(text=text, mention=Mention(mentionees=ments))
        else:
            msg = TextSendMessage(text=text, mention={"mentionees": mentionees})
    else:
        msg = TextSendMessage(text=text)
    BOT.push_message(GROUP, msg)

def send_to(group_id, text, mentionees=None):
    """任意グループへ送信（GROUP2で使用）"""
    _ensure_bot_initialized()
    if mentionees:
        if USE_OBJ:
            ments = [
                (Mentionee(type="all", index=m["index"], length=m["length"])
                 if m.get("type") == "all"
                 else Mentionee(type="user", user_id=m["userId"],
                                index=m["index"], length=m["length"]))
                for m in mentionees
            ]
            msg = TextSendMessage(text=text, mention=Mention(mentionees=ments))
        else:
            msg = TextSendMessage(text=text, mention={"mentionees": mentionees})
    else:
        msg = TextSendMessage(text=text)
    BOT.push_message(group_id, msg)


# ============= 通知ジョブ群 =============
def d_0600():
    at = "@石橋和大"
    txt = f"{at}\n日本の朝6時です、P活ルーティンをせよ。"
    send(txt, [{"type": "user", "userId": KAZUO, "index": 0, "length": len(at)}])

def d_1200():
    at = "@all"; txt = f"{at}\n昼12時、昼のWEB講演会あるかもよ。"
    send(txt, [{"type": "all", "index": 0, "length": len(at)}])

def d_1800():
    at = "@all"; txt = f"{at}\n夕18時、WEB講演会大丈夫かい。"
    send(txt, [{"type": "all", "index": 0, "length": len(at)}])

def d_2100():
    at_all = "@all"; at_y = "@石橋夕稀子"
    txt = (f"{at_all}\n夜21時、夜のルーティンね。\n"
           f"{at_y}\nいつものアンケート案件よろしく。\n（m3, プラメド、 Medure、日経、care）")
    send(txt, [
        {"type": "all", "index": 0, "length": len(at_all)},
        {"type": "user", "userId": YUKIKO, "index": txt.find(at_y), "length": len(at_y)}
    ])

def w_sat_1500():
    at = "@石橋夕稀子"
    txt = (f"{at}\nプラメドの締め切りが近いです。よろしくお願いいたします。\n"
           "https://docs.google.com/spreadsheets/d/1qdYP3TIUQIyzYyYukpvtrF3EsBT2uM8gDtxiTgpCMkY/edit?gid=1676746958#gid=1676746958")
    send(txt, [{"type": "user", "userId": YUKIKO, "index": 0, "length": len(at)}])

def m_28_0900():
    at = "@石橋夕稀子"
    txt = (f"{at}\nm3の締め切りが近いです。よろしくお願いいたします。\n"
           "https://docs.google.com/spreadsheets/d/1qdYP3TIUQIyzYyYukpvtrF3EsBT2uM8gDtxiTgpCMkY/edit?gid=1676746958#gid=1676746958")
    send(txt, [{"type": "user", "userId": YUKIKO, "index": 0, "length": len(at)}])

def m_02_0900():
    at = "@石橋夕稀子"
    txt = (f"{at}\nIQVIAの締め切りが近いです。よろしくお願いいたします。\n"
           "https://docs.google.com/spreadsheets/d/1qdYP3TIUQIyzYyYukpvtrF3EsBT2uM8gDtxiTgpCMkY/edit?gid=1676746958#gid=1676746958")
    send(txt, [{"type": "user", "userId": YUKIKO, "index": 0, "length": len(at)}])

# GROUP2
def d_0700_group2():
    at = "@all"
    txt = (f"{at}\n毎朝7時。\n"
           "朝活してますか？日光浴びてますか？深呼吸できてますか？\n"
           "セコムしてますか？")
    send_to(GROUP2, txt, [{"type": "all", "index": 0, "length": len(at)}])

def d_2200_group2():
    at_all = "@all"; at_k = "@石橋和大"
    txt = (f"{at_all}\n毎晩22時。\n"
           f"{at_k}\nそろそろ閉業の準備ね。23時までには\n"
           "ストレッチ、片付け、明日準備、必ずね。\n"
           "今日もお疲れ様でした。")
    send_to(GROUP2, txt, [
        {"type": "all", "index": 0, "length": len(at_all)},
        {"type": "user", "userId": KAZUO, "index": txt.find(at_k), "length": len(at_k)}
    ])


# ============= スケジューラ起動（Render無料での要） =============
def start_scheduler():
    """
    Render(無料)のWeb起動時に一度だけ呼ぶ。
    - .env/環境変数をここで読み込む（import時に落ちないように）
    - APScheduler(Background) を起動して常駐
    """
    global _STARTED, SCHED, BOT, GROUP, GROUP2, KAZUO, YUKIKO
    if _STARTED:
        return  # 二重起動ガード

    load_dotenv()
    token  = os.getenv("CHANNEL_ACCESS_TOKEN")
    group  = os.getenv("GROUP_ID_MAIN")
    group2 = os.getenv("GROUP_ID_SECOND")
    kazuo  = os.getenv("USER_ID_KAZUO")
    yukiko = os.getenv("USER_ID_YUKIKO")

    missing = [k for k, v in {
        "CHANNEL_ACCESS_TOKEN": token,
        "GROUP_ID_MAIN": group,
        "GROUP_ID_SECOND": group2,
        "USER_ID_KAZUO": kazuo,
        "USER_ID_YUKIKO": yukiko,
    }.items() if not v]
    if missing:
        # import時に落とさず、起動時にだけ明示エラー
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

    # グローバルに反映
    BOT = LineBotApi(token)
    GROUP, GROUP2, KAZUO, YUKIKO = group, group2, kazuo, yukiko

    # スケジューラ
    SCHED = BackgroundScheduler(timezone="Asia/Tokyo")
    # 毎日
    SCHED.add_job(d_0600, CronTrigger(hour=6))
    SCHED.add_job(d_1200, CronTrigger(hour=12))
    SCHED.add_job(d_1800, CronTrigger(hour=18))
    SCHED.add_job(d_2100, CronTrigger(hour=21))
    # 毎週・毎月
    SCHED.add_job(w_sat_1500, CronTrigger(day_of_week="sat", hour=15))
    SCHED.add_job(m_28_0900, CronTrigger(day="28", hour=9))
    SCHED.add_job(m_02_0900, CronTrigger(day="2", hour=9))
    # GROUP2
    SCHED.add_job(d_0700_group2, CronTrigger(hour=7))
    SCHED.add_job(d_2200_group2, CronTrigger(hour=22))

    SCHED.start()
    _STARTED = True
    print("Scheduler started (JST)")


# ============= ローカルで python scheduler.py 実行時 =============
if __name__ == "__main__":
    start_scheduler()
    while True:
        time.sleep(3600)
