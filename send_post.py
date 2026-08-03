import requests
import os
from datetime import datetime

print("=== شاهنامه بات v5 - تلاش هوشمند تا دریافت فردوسی ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GANJOOR_API = "https://api.ganjoor.net/api/ganjoor"

def get_shahnameh_verses(max_retries=15):
    for attempt in range(1, max_retries + 1):
        try:
            url = f"{GANJOOR_API}/poem/random"
            r = requests.get(url, params={"poetId": 2}, timeout=12)
            r.raise_for_status()
            poem = r.json()

            poet = poem.get('poet', {})
            poet_name = poet.get('name', 'نامشخص')
            poet_id = poet.get('id')

            print(f"تلاش {attempt}: شاعر = {poet_name} (ID: {poet_id})")

            if poet_id == 2 or "فردوسی" in poet_name or "فردوسي" in poet_name:
                verses = poem.get('verses', [])
                title = poem.get('title', 'شاهنامه')
                full_url = f"https://ganjoor.net{poem.get('fullUrl', '')}"
                print(f"✅ بیت از شاهنامه دریافت شد!")
                return verses[:4], title, full_url

        except Exception as e:
            print(f"خطا در تلاش {attempt}: {e}")

    print("❌ بعد از ۱۵ تلاش هم بیت از شاهنامه پیدا نشد")
    return None, None, None

def create_caption(verses, title):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        caption += f"{verse.get('text', '')}\n"
    
    caption += f"\n🏷️ {title}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption

def send_post():
    verses, title, poem_url = get_shahnameh_verses()

    if not verses:
        return

    caption = create_caption(verses, title)

    keyboard = {
        "inline_keyboard": [
            [{"text": "📖 خواندن کامل این بخش", "url": poem_url}],
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
