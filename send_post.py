import requests
import os
from datetime import datetime

print("=== شاهنامه بات v3 - فقط فردوسی + دکمه درست ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GANJOOR_API = "https://api.ganjoor.net/api/ganjoor"

def get_shahnameh_verses(count=4):
    try:
        # روش مطمئن‌تر برای دریافت فقط از شاهنامه
        url = f"{GANJOOR_API}/poet/2/random"
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        poem = r.json()
        
        verses = poem.get('verses', [])
        title = poem.get('title', 'شاهنامه')
        full_url = f"https://ganjoor.net{poem.get('fullUrl', '')}"
        
        print(f"شعر دریافت شده از: {title}")
        print(f"تعداد بیت: {len(verses)}")
        
        return verses[:count], poem, full_url
    except Exception as e:
        print(f"خطا در دریافت بیت: {e}")
        return None, None, None

def create_caption(verses, title):
    caption = "📖 **شاهنامه فردوسی**\n\n"
    for verse in verses:
        caption += f"{verse.get('text', '')}\n"
    
    caption += f"\n🏷️ {title}"
    caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"
    return caption

def send_post():
    verses, poem, poem_url = get_shahnameh_verses(count=4)

    if not verses or not poem:
        print("❌ نتوانست بیت از شاهنامه دریافت کند")
        return

    caption = create_caption(verses, poem.get('title', 'شاهنامه'))

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📖 خواندن کامل داستان", "url": poem_url}
            ],
            [
                {"text": "🎧 شنیدن صوت", "url": poem_url},
                {"text": "📖 شرح و معنی", "url": poem_url + "#meaning"}
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
        print("✅ پست شاهنامه با موفقیت ارسال شد")
    else:
        print(f"❌ خطا در ارسال: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
