import os
import requests
import yfinance as yf
import feedparser
from datetime import datetime

TELEGRAM_TOKEN = os.environ[“TELEGRAM_TOKEN”]
CHAT_ID = os.environ[“TELEGRAM_CHAT_ID”]
PRICE_LEVELS = [420, 400, 380, 360]
TICKER = “MC.PA”

def send_telegram(message):
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {
“chat_id”: CHAT_ID,
“text”: message,
“parse_mode”: “HTML”,
“disable_web_page_preview”: False
}
requests.post(url, json=payload)

# ─── ALERT 1: Preț LVMH ───────────────────────────────────────────────

def check_price():
ticker = yf.Ticker(TICKER)
data = ticker.history(period=“1d”, interval=“15m”)
if data.empty:
return
price = round(data[“Close”].iloc[-1], 2)
print(f”Preț curent LVMH: {price} EUR”)

```
for level in PRICE_LEVELS:
    if price < level:
        msg = (
            f"⚠️ <b>LVMH (MC.PA) sub {level} EUR</b>\n"
            f"Preț curent: <b>{price} EUR</b>\n"
            f"📅 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC"
        )
        send_telegram(msg)
        print(f"Alertă trimisă: sub {level}")
        break  # trimite o singură alertă per run (cel mai jos nivel atins)
```

# ─── ALERT 2 & 3: Anunțuri AMF + Rezultate financiare ─────────────────

AMF_RSS = “https://www.amf-france.org/fr/rss/actualites”
LVMH_KEYWORDS = [“lvmh”, “moët hennessy”, “mc.pa”, “christian dior”]
RESULTS_KEYWORDS = [“résultats”, “chiffre d’affaires”, “résultats annuels”,
“résultats semestriels”, “results”, “revenue”, “earnings”]

def fetch_consensus():
“”“Preia EPS estimat de la Yahoo Finance”””
try:
ticker = yf.Ticker(TICKER)
info = ticker.info
eps_est = info.get(“epsForward”, “N/A”)
revenue_est = info.get(“revenueEstimatesAvg”, “N/A”)
return eps_est, revenue_est
except Exception:
return “N/A”, “N/A”

def fetch_actual_results(entry):
“”“Încearcă să extragă cifre din titlul/sumarul anunțului”””
return entry.get(“summary”, “Vezi linkul pentru detalii.”)

def check_amf_announcements():
feed = feedparser.parse(AMF_RSS)
for entry in feed.entries:
title_lower = entry.title.lower()
summary_lower = entry.get(“summary”, “”).lower()

```
    # Verifică dacă e despre LVMH
    is_lvmh = any(kw in title_lower or kw in summary_lower for kw in LVMH_KEYWORDS)
    if not is_lvmh:
        continue

    link = entry.get("link", "")
    published = entry.get("published", "")

    # Verifică dacă e anunț de rezultate financiare
    is_results = any(kw in title_lower or kw in summary_lower for kw in RESULTS_KEYWORDS)

    if is_results:
        eps_est, rev_est = fetch_consensus()
        actual_summary = fetch_actual_results(entry)
        msg = (
            f"📊 <b>LVMH – Rezultate Financiare</b>\n"
            f"📌 {entry.title}\n\n"
            f"<b>Consens estimat (Yahoo Finance):</b>\n"
            f"  EPS forward: {eps_est}\n"
            f"  Revenue est.: {rev_est}\n\n"
            f"<b>Rezumat anunț:</b>\n{actual_summary[:400]}\n\n"
            f"🔗 <a href='{link}'>Vezi anunțul complet</a>\n"
            f"📅 {published}"
        )
    else:
        msg = (
            f"📢 <b>LVMH – Anunț obligatoriu AMF</b>\n"
            f"📌 {entry.title}\n\n"
            f"🔗 <a href='{link}'>Vezi anunțul</a>\n"
            f"📅 {published}"
        )

    send_telegram(msg)
    print(f"Alertă AMF trimisă: {entry.title}")
```

# ─── MAIN ──────────────────────────────────────────────────────────────

if **name** == “**main**”:
print(”=== LVMH Alert Bot ===”)
check_price()
check_amf_announcements()
print(”=== Done ===”)
