import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - API گنجور (نسخه بهینه v20) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BITS_PER_POST = 6

def get_ferdowsi_poem():
    """تلاش برای دریافت بیت فقط از فردوسی"""
    for attempt in range(8):
        try:
            url = "https://api.ganjoor.net/api/ganjoor/poem/random"
            params = {"poetId": 2}
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            poem = r.json()

            poet_id = poem.get('poet', {}).get('id') or poem.get('poetId')
            poet_name = poem.get('poet', {}).get('name', '')

            if poet_id == 2 or "فردوسی" in poet_name or "فردوسي" in poet_name:
                verses = poem.get('verses', [])
                title = poem.get('title', 'شاهنامه')
                full_url = f"https://ganjoor.net{poem.get('fullUrl', '')}"
                print(f"✅ بیت از فردوسی دریافت شد (تلاش {attempt+1})")
                return verses[:BITS_PER_POST], title, full_url
            else:
                print(f"تلاش {attempt+1}: دریافت از {poet_name} - دوباره تلاش میکنم")
                continue
        except Exception as e:
            print(f"خطا در تلاش {attempt+1}: {e}")
            continue

    print("❌ بعد از چندین تلاش بیت از فردوسی دریافت نشد")
    return None, None, None

def create_caption(verses, title):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        if verse.get('text'):
            caption += f"{verse.get('text')}\n"
    
    caption += f"\n🏷️ {title}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    caption += "\n\n🔹 از API گنجور"
    return caption

def send_post():
    verses, title, poem_url = get_ferdowsi_poem()

    if not verses:
        print("ارسال متوقف شد")
        return

    caption = create_caption(verses, title)

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📖 ادامه خواندن", "url": poem_url}
            ],
            [
                {"text": "🎧 صوت خوانش", "url": poem_url},
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
        print(f"❌ خطا در ارسال: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
