import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - ارسال متن (نسخه نهایی) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BITS_PER_POST = 6
FILE_NAME = "shahnameh.txt"

def load_state():
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                return json.load(f).get("last_index", 0)
        except:
            return 0
    return 0

def save_state(last_index):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({"last_index": last_index}, f, ensure_ascii=False, indent=2)

def load_shahnameh():
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return lines

def create_caption(verses, start_index):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        caption += f"{verse}\n\n"
    
    caption += f"📍 بیت {start_index + 1} تا {start_index + len(verses)}\n"
    caption += f"📅 {datetime.now().strftime('%Y/%m/%d')}\n"
    caption += "\n🔹 تصحیح نزدیک به جلال خالقی مطلق"
    return caption

def send_post():
    state = load_state()
    shahnameh = load_shahnameh()
    
    start = state
    verses = shahnameh[start:start + BITS_PER_POST]

    if not verses:
        print("به پایان شاهنامه رسیدیم. از ابتدا شروع می‌شود.")
        save_state(0)
        return

    caption = create_caption(verses, start)

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🎧 صوت شاهنامه", "url": "https://www.youtube.com/results?search_query=صوت+خوانندگی+شاهنامه+فردوسی"},
                {"text": "📚 درباره شاهنامه", "url": "https://fa.wikipedia.org/wiki/شاهنامه"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"✅ ارسال شد: بیت {start+1} تا {start+len(verses)}")
        save_state(start + len(verses))
    else:
        print("❌ خطا:", response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده")
    else:
        send_post()
