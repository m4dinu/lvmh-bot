import os, requests, yfinance as yf, feedparser
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
LEVELS = [420, 400, 380, 360]

def send(msg):
    requests.post(
        "https://api.telegram.org/bot" + TOKEN + "/sendMessage",
        json={"chat_id": CHAT, "text": msg}
    )

def check_price():
    data = yf.Ticker("MC.PA").history(period="1d", interval="15m")
    if data.empty:
        return
    price = round(data["Close"].iloc[-1], 2)
    print(price)
    for lvl in LEVELS:
        if price < lvl:
            send("LVMH sub " + str(lvl) + " EUR. Pret: " + str(price) + " EUR")
            break

def check_amf():
    feed = feedparser.parse("https://www.amf-france.org/fr/rss/actualites")
    for e in feed.entries:
        t = e.title.lower()
        if "lvmh" in t or "moet" in t:
            send("LVMH - AMF: " + e.title + "\n" + e.get("link", ""))

if __name__ == "__main__":
    check_price()
    check_amf()
    print("done")
