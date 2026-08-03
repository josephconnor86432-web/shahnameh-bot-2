import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - نسخه متنی (ترتیبی) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

# ================= تنظیمات =================
BITS_PER_POST = 4          # تعداد بیت در هر پست
FILE_NAME = "shahnameh.txt"

def load_state():
    if os.path.exists("state.json"):
        with open("state.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_index": 0}

def save_state(last_index):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({"last_index": last_index}, f, ensure_ascii=False, indent=2)

def load_shahnameh():
    if not os.path.exists(FILE_NAME):
        print(f"❌ فایل {FILE_NAME} پیدا نشد!")
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def create_caption(verses, start_index):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        caption += f"{verse}\n"
    
    caption += f"\n📍 بیت {start_index + 1} تا {start_index + len(verses)}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption

def send_post():
    state = load_state()
    shahnameh = load_shahnameh()
    
    if not shahnameh:
        print("فایل شاهنامه خالی یا وجود ندارد")
        return

    start = state["last_index"]
    end = start + BITS_PER_POST
    verses = shahnameh[start:end]

    if not verses:
        print("به پایان شاهنامه رسیدیم! از ابتدا شروع می‌شود.")
        state["last_index"] = 0
        save_state(0)
        return

    caption = create_caption(verses, start)

    # دکمه‌ها
    keyboard = {
        "inline_keyboard": [
            [{"text": "⏭ بیت بعدی", "callback_data": "next"}],
            [
                {"text": "🎧 صوت شاهنامه", "url": "https://ganjoor.net/ferdowsi/shahname"},
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
        print(f"✅ پست ارسال شد (بیت {start+1} تا {start+len(verses)})")
        save_state(end)
    else:
        print("❌ خطا در ارسال:", response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده")
    else:
        send_post()
