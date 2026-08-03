import requests
import json
import os
from datetime import datetime

print("=== شاهنامه بات - نسخه نهایی v11 (لینک‌های اصلاح شده) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
BITS_PER_POST = 4
FILE_NAME = "shahnameh.txt"

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
        print("به پایان شاهنامه رسیدیم.")
        save_state(0)
        return

    caption = create_caption(verses, start)

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "📖 ادامه خواندن شاهنامه", 
                 "url": "https://ganjoor.net/ferdowsi/shahname/"}
            ],
            [
                {"text": "🎧 صوت‌های شاهنامه", 
                 "url": 
