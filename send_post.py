import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - نسخه نهایی (متن + عکس) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BITS_PER_POST = 4
FILE_NAME = "shahnameh.txt"

# لینک تصویر ثابت از ویکی‌پدیا (مستقیم و تست‌شده)
IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Shahnameh_The_Houghton_01.jpg/800px-Shahnameh_The_Houghton_01.jpg"

def load_state():
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                return {"last_index": int(json.load(f).get("last_index", 0))}
        except:
            return {"last_index": 0}
    return {"last_index": 0}

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
        caption += f"{verse}\n"
    
    caption += f"\n📍 بیت {start_index + 1} تا {start_index + len(verses)}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption

def send_post():
    state = load_state()
    shahnameh = load_shahnameh()
    
    start = state["last_index"]
    verses = shahnameh[start:start + BITS_PER_POST]

    if not verses:
        print("به پایان شاهنامه رسیدیم. ریست شد.")
        save_state(0)
        return

    caption = create_caption(verses, start)

    # فقط دکمه‌هایی که ۱۰۰٪ کار می‌کنند
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🎧 صوت شاهنامه", 
                 "url": "https://www.youtube.com/results?search_query=%D8%B5%D9%88%D8%AA+%D8%AE%D9%88%D8%A7%D9%86%D8%AF%DA%AF%DB%8C+%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87"},
                {"text": "🔎 درباره شاهنامه", 
                 "url": "https://fa.wikipedia.org/wiki/%D8%B4%D8%A7%D9%87%D9%86%D8%A7%D9%85%D9%87"}
            ]
        ]
    }

    # ارسال عکس + متن با هم
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": IMAGE_URL,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(f"✅ پست با عکس ارسال شد (بیت {start+1} تا {start+len(verses)})")
        save_state(start + len(verses))
    else:
        print(f"❌ خطا در ارسال عکس: {response.status_code} - {response.text}")
        # اگر عکس مشکل داشت، فقط متن ارسال شود
        url_text = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload_text = {
            "chat_id": CHANNEL_ID,
            "text": caption + "\n\n📷 [تصویر شاهنامه](https://upload.wikimedia.org/wikipedia/commons/9/9f/Shahnameh_The_Houghton_01.jpg)",
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(keyboard)
        }
        response_text = requests.post(url_text, json=payload_text)
        if response_text.status_code == 200:
            print("✅ پست متنی (بدون عکس) ارسال شد")
            save_state(start + len(verses))
        else:
            print(f"❌ خطا در ارسال متن هم: {response_text.status_code}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
