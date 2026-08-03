import requests
import os
from datetime import datetime

print("=== شاهنامه بات v2 - دکمه‌های بهبود یافته ===")

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
        print(f"شعر دریافت شده: {poem.get('title', 'نامشخص')}")
        return verses[:count], poem
    except Exception as e:
        print(f"خطا در دریافت بیت: {e}")
        return None, None

def create_caption(verses, poem):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    
    for verse in verses:
        caption += f"{verse.get('text', '')}\n"
    
    caption += f"\n🏷️ {poem.get('title', 'شاهنامه')}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption

def send_post():
    verses, poem = get_random_verses(count=4)

    if not verses or not poem:
        print("❌ نتوانست بیت دریافت کند")
        return

    caption = create_caption(verses, poem)
    poem_url = f"https://ganjoor.net{poem.get('fullUrl', '')}"

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📖 خواندن کامل غزل/قطعه", "url": poem_url}
            ],
            [
                {"text": "🎧 شنیدن صوت", "url": poem_url},
                {"text": "🔎 معنی و شرح", "url": poem_url}
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
        print("✅ پست با موفقیت ارسال شد")
        print(f"لینک استفاده شده: {poem_url}")
    else:
        print(f"❌ خطا در ارسال: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
