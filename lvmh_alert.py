import os
import requests
import yfinance as yf
import feedparser
from datetime import datetime

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
PRICE_LEVELS = [420, 400, 380, 360]
TICKER = "MC.PA"

def send_telegram(message):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def check_price():
    ticker = yf.Ticker(TICKER)
    data = ticker.history(period="1d", interval="15m")
    if data.empty:
        return
    price = round(data["Close"].iloc[-1], 2)
    print("Pret curent LVMH: " + str(price) + " EUR")

    for level in PRICE_LEVELS:
        if price < level:
            msg = (
                "LVMH (MC.PA) sub " + str(level) + " EUR\n"
                "Pret curent: " + str(price) + " EUR\n"
                "Data: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M") + " UTC"
            )
            send_telegram(msg)
            print("Alerta trimisa: sub " + str(level))
            break

AMF_RSS = "https://www.amf-france.org/fr/rss/actualites"
LVMH_KEYWORDS = ["lvmh", "moet hennessy", "mc.pa", "christian dior"]
RESULTS_KEYWORDS = ["resultats", "chiffre d affaires", "results", "revenue", "earnings"]

def fetch_consensus():
    try:
        ticker = yf.Ticker(TICKER)
        info = ticker.info
        eps_est = info.get("epsForward", "N/A")
