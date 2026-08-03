import requests
import os
from datetime import datetime

print("=== نسخه بدون عکس شروع به کار کرد ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GANJOOR_API = "https://api.ganjoor.net/api/ganjoor"

def get_random_verses(count=4):
    try:
        url = f"{GANJOOR_API}/poem/random"
        params = {"poetId": 2}
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        poem = r.json()
        verses = poem.get('verses', [])
        print(f"تعداد بیت دریافت شده: {len(verses)}")
        return verses[:count]
    except Exception as e:
        print(f"خطا در دریافت بیت: {e}")
        return None

def create_caption(verses):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        caption += f"{verse.get('text', '')}\n"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption

def send_post():
    verses = get_random_verses(count=4)

    if not verses or len(verses) < 2:
        print("❌ نتوانست بیت دریافت کند")
        return

    caption = create_caption(verses)

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🎤 صوت خوانش", "url": f"https://ganjoor.net{verses[0].get('poem', {}).get('fullUrl', '')}"},
                {"text": "📖 ادامه داستان", "url": f"https://ganjoor.net{verses[0].get('poem', {}).get('fullUrl', '')}"}
            ],
            [
                {"text": "🔎 شرح و معنی", "url": f"https://ganjoor.net{verses[0].get('poem', {}).get('fullUrl', '')}"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": caption,
        "parse_mode": "Markdown",
        "reply_markup": str(keyboard).replace("'", '"')
    }

    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ پست با موفقیت به کانال ارسال شد")
    else:
        print(f"❌ خطا در ارسال: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
