import requests
import json
import os
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GANJOOR_API = "https://api.ganjoor.net/api/ganjoor"

# لینک‌های مستقیم و مطمئن‌تر تصاویر
IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/9/9f/Shahnameh_The_Houghton_01.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/5/5e/Rostam_and_Sohrab.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/7/7e/Shahnameh_-_Rustam_and_the_White_Div.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/0/0d/Bijan_and_Manijeh.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/8/8f/Ferdowsi_-_Shahnameh_-_The_Court_of_Gayumars.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/3/3f/Shahnameh_-_Zal_and_the_Simurgh.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Shahnameh_illustration.jpg/1280px-Shahnameh_illustration.jpg"
]

def load_state():
    if os.path.exists("state.json"):
        with open("state.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_image_index": 0}

def save_state(state):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def get_random_verses(count=4):
    try:
        url = f"{GANJOOR_API}/poem/random"
        params = {"poetId": 2}
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        poem = r.json()
        verses = poem.get('verses', [])
        return verses[:count] if verses else None
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
    state = load_state()
    verses = get_random_verses(count=4)

    if not verses or len(verses) < 2:
        print("❌ نتوانست بیت دریافت کند")
        return

    caption = create_caption(verses)
    image_index = state["last_image_index"] % len(IMAGES)
    image_url = IMAGES[image_index]
    
    print(f"در حال ارسال تصویر شماره: {image_index + 1}")
    print(f"لینک تصویر: {image_url}")

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🎤 صوت خوانش", "url": f"https://ganjoor.net{verses[0].get('poem', {}).get('fullUrl', '')}"},
                {"text": "📖 ادامه داستان", "url": f"https://ganjoor.net{verses[0].get('poem', {}).get('fullUrl', '')}"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": json.dumps(keyboard)
    }

    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("✅ پست با موفقیت ارسال شد")
        state["last_image_index"] += 1
        save_state(state)
    else:
        print(f"❌ خطا در ارسال به تلگرام: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ BOT_TOKEN یا CHANNEL_ID تنظیم نشده است")
    else:
        send_post()
