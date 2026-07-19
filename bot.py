"""
Telegram İslami Bilgi Botu
---------------------------
GitHub Actions tarafından saatte bir (09:00-21:00, İstanbul saati) tetiklenir.
Tetiklendiği saate göre ya bir hadis ya da bir fıkıh bilgisi gönderir,
gönderdiği kaydın indeksini state.json içinde ilerletir.

09,11,13,15,17,19,21 -> Hadis  (7 gönderi)
10,12,14,16,18,20    -> Fıkıh  (6 gönderi)
"""

import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import BOT_TOKEN, CHAT_ID

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, "state.json")
HADIS_FILE = os.path.join(BASE_DIR, "data", "hadis.json")
FIKIH_FILE = os.path.join(BASE_DIR, "data", "fikih.json")

HADIS_HOURS = {9, 11, 13, 15, 17, 19, 21}
FIKIH_HOURS = {10, 12, 14, 16, 18, 20}

TELEGRAM_MAX_LEN = 4096


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"fikih_index": 0, "hadis_index": 0}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def format_hadis(item):
    parts = [f"📖 *{item['title']}*", ""]
    parts.append(item["hadith"])
    parts.append("")
    parts.append(f"_Ravi: {item['narrator']}_")
    parts.append(f"Kaynak: {item['source']}")
    if item.get("comment"):
        parts.append("")
        parts.append(f"💡 {item['comment']}")
    return "\n".join(parts)


def format_fikih(item):
    parts = [f"⚖️ *{item['title']}*", ""]
    parts.append(item["text"])
    parts.append("")
    parts.append(f"Kaynak: {item['source']}")
    return "\n".join(parts)


def send_message(text):
    if len(text) > TELEGRAM_MAX_LEN:
        text = text[: TELEGRAM_MAX_LEN - 20] + "\n\n(...devamı kısaltıldı)"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    resp = requests.post(url, data=payload, timeout=30)
    if resp.status_code != 200:
        print("TELEGRAM HATA DETAYI:", resp.text)
    resp.raise_for_status()
    return resp.json()


def main():
    now_tr = datetime.now(ZoneInfo("Europe/Istanbul"))
    hour = now_tr.hour

    # Manuel test için: workflow_dispatch ile FORCE_HOUR verilirse onu kullan
    forced = os.environ.get("FORCE_HOUR")
    if forced is not None:
        hour = int(forced)

    if hour in HADIS_HOURS:
        content_type = "hadis"
    elif hour in FIKIH_HOURS:
        content_type = "fikih"
    else:
        print(f"Saat {hour}:00, gönderim penceresi (09-21) dışında. Çıkılıyor.")
        sys.exit(0)

    state = load_state()

    if content_type == "hadis":
        data = load_json(HADIS_FILE)
        idx = state["hadis_index"] % len(data)
        item = data[idx]
        text = format_hadis(item)
        state["hadis_index"] = (idx + 1) % len(data)
    else:
        data = load_json(FIKIH_FILE)
        idx = state["fikih_index"] % len(data)
        item = data[idx]
        text = format_fikih(item)
        state["fikih_index"] = (idx + 1) % len(data)

    send_message(text)
    save_state(state)
    print(f"[{now_tr.isoformat()}] {content_type} gönderildi. Yeni state: {state}")


if __name__ == "__main__":
    main()
