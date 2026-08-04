import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - API گنجور (نسخه调试 v21) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BITS_PER_POST = 6

def get_shahnameh_verses():
    try:
        # روش جدید: استفاده از endpoint خاص شاهنامه
        url = "https://api.ganjoor.net/api/ganjoor/poem/random"
        params = {"poetId": 2}
        
        r = requests.get(url, params=params, timeout=20)
        print(f"Status Code: {r.status_code}")
        
        data = r.json()
        print("ساختار دریافتی از API:")
        print(json.dumps(data, ensure_ascii=False, indent=2)[:800] + "...")  # لاگ محدود

        # بررسی چندین روش ممکن برای تشخیص فردوسی
        poet_id = None
        if isinstance(data, dict):
            poet_id = data.get('poetId') or data.get('poet', {}).get('id')
            poet_name = data.get('poet', {}).get('name', '') or data.get('poetName', '')

        if poet_id == 2 or "فردوسی" in str(poet_name) or "فردوسي" in str(poet_name):
            verses = data.get('verses', [])
            title = data.get('title', 'شاهنامه')
            full_url = f"https://ganjoor.net{data.get('fullUrl', '')}"
            print(f"✅ بیت از شاهنامه دریافت شد")
            return verses[:BITS_PER_POST], title, full_url
        else:
            print(f"⚠️ دریافت شده از: {poet_name} (ID: {poet_id})")
            return None, None, None

    except Exception as e:
        print(f"خطای کلی: {e}")
        return None, None, None


def create_caption(verses, title):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        if verse and verse.get('text'):
            caption += f"{verse.get('text')}\n"
    
    caption += f"\n🏷️ {title}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption


def send_post():
    verses, title, poem_url = get_shahnameh_verses()

    if not verses:
        print("❌ نتوانست بیت مناسب دریافت کند")
        return

    caption = create_caption(verses, title)

    keyboard = {
        "inline_keyboard": [
            [{"text": "📖 خواندن کامل در گنجور", "url": poem_url}],
            [
                {"text": "🎧 صوت", "url": poem_url},
                {"text": "🔎 شرح و معنی", "url": poem_url}
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
        print("✅ پست با موفقیت ارسال شد")
    else:
        print(f"❌ خطا در ارسال به تلگرام: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا CHANNEL_ID تنظیم نشده")
    else:
        send_post()
