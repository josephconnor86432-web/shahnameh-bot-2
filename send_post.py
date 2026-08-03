import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - نسخه تمیز v8 ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BITS_PER_POST = 4
FILE_NAME = "shahnameh.txt"

def load_state():
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return {"last_index": int(data.get("last_index", 0))}
        except:
            return {"last_index": 0}
    return {"last_index": 0}

def save_state(last_index):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({"last_index": last_index}, f, ensure_ascii=False, indent=2)

def load_shahnameh():
    if not os.path.exists(FILE_NAME):
        print(f"❌ فایل {FILE_NAME} پیدا نشد!")
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
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
        print("❌ فایل شاهنامه خالی است")
        return

    # برای تست فعلاً همیشه از اول شروع کند (بعداً برمی‌داریم)
    start = 0
    verses = shahnameh[start:start + BITS_PER_POST]

    if not verses:
        print("فایل شاهنامه خیلی کوتاه است")
        return

    caption = create_caption(verses, start)

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📖 ادامه خواندن در گنجور", 
                 "url": "https://ganjoor.net/ferdowsi/shahname/"}
            ],
            [
                {"text": "🎧 صوت‌های شاهنامه", 
                 "url": "https://ganjoor.net/ferdowsi/shahname"},
                {"text": "📚 شاهنامه کامل (PDF)", 
                 "url": "https://github.com/josephconnor86432-web/shahnameh-bot-2/raw/main/shahnameh.pdf"}
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
        save_state(start + len(verses))
    else:
        print(f"❌ خطا در ارسال: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
