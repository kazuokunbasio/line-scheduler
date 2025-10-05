# app.py（検証用の最小サーバ）
from flask import Flask, request
app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    return "OK", 200  # 返事が200なら検証は通る

if __name__ == "__main__":
    app.run("0.0.0.0", 8000)
