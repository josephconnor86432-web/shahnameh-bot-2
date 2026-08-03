import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات v4 - endpoint درست + تکرار تا فردوسی ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GANJOOR_API = "https://api.ganjoor.net/api/ganjoor"

def get_shahnameh_verses(max_retries=6):
    for attempt in range(max_retries):
        try:
            url = f"{GANJOOR_API}/poem/random"
            params = {"poetId": 2}   # فقط فردوسی
            r = requests.get(url, params=params, timeout=15)
            r.raise_for_status()
            poem = r.json()
            
            # چک کردن اینکه واقعاً از فردوسی باشد
            if poem.get('poet', {}).get('id') == 2 or poem.get('poetId') == 2:
                verses = poem.get('verses', [])
                title = poem.get('title', 'شاهنامه')
                full_url = f"https://ganjoor.net{poem.get('fullUrl', '')}"
                print(f"✅ بیت از شاهنامه دریافت شد | تلاش {attempt+1}")
                return verses[:4], title, full_url
            else:
                print(f"تلاش {attempt+1}: شعر از فردوسی نبود، دوباره تلاش میکنم...")
                continue
                
        except Exception as e:
            print(f"خطا در تلاش {attempt+1}: {e}")
            continue
    
    print("❌ بعد از چندین تلاش نتوانست بیت از شاهنامه بگیرد")
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
        print("✅ پست شاهنامه با موفقیت به کانال ارسال شد")
    else:
        print(f"❌ خطا در ارسال پیام: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ BOT_TOKEN یا CHANNEL_ID تنظیم نشده است")
    else:
        send_post()
