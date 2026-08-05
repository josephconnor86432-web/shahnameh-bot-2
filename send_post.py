import requests
import json
import os
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract

print("=== شاهنامه خالقی مطلق - نسخه نهایی (۳ صفحه در هر پست) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAGES_PER_POST = 3   # کاهش یافته برای جلوگیری از ارور طول پیام

PDF_FILES = [
    "شاهنامه_فردوسی_به_تصحیح_جلال_خالقی_مطلق_نسخه_کامل_هشت_جلدی_compressed-1.pdf",
    "شاهنامه_فردوسی_به_تصحیح_جلال_خالقی_مطلق_نسخه_کامل_هشت_جلدی_compressed-2.pdf",
    "شاهنامه_فردوسی_به_تصحیح_جلال_خالقی_مطلق_نسخه_کامل_هشت_جلدی_compressed-3.pdf",
    "شاهنامه_فردوسی_به_تصحیح_جلال_خالقی_مطلق_نسخه_کامل_هشت_جلدی_compressed-4.pdf",
    "شاهنامه_فردوسی_به_تصحیح_جلال_خالقی_مطلق_نسخه_کامل_هشت_جلدی_compressed-5.pdf"
]

def load_state():
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("current_file", 0), data.get("current_page", 36)
        except:
            return 0, 36
    return 0, 36

def save_state(current_file, current_page):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({"current_file": current_file, "current_page": current_page}, f, ensure_ascii=False, indent=2)

def clean_text(text):
    if not text:
        return ""
    # پاکسازی کاراکترهای مشکل‌ساز
    text = text.replace('*', '∗').replace('_', 'ـ').replace('`', "'").replace('**', '').replace('__', '')
    text = text.replace('\n\n\n', '\n\n').strip()
    return text

def send_post():
    current_file_idx, current_page = load_state()
    
    if current_file_idx >= len(PDF_FILES):
        print("تمام فایل‌ها پردازش شدند.")
        return

    pdf_path = PDF_FILES[current_file_idx]
    if not os.path.exists(pdf_path):
        print(f"فایل پیدا نشد: {pdf_path}")
        return

    print(f"در حال پردازش فایل {current_file_idx + 1}/5 - صفحه {current_page + 1} به بعد")

    try:
        images = convert_from_path(pdf_path, dpi=180, first_page=current_page + 1, 
                                 last_page=current_page + PAGES_PER_POST)

        full_text = ""
        sent_pages = 0

        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang='fas', config='--psm 6')
            cleaned = clean_text(text)
            if cleaned:
                full_text += f"📌 صفحه {current_page + i + 1}\n\n{cleaned}\n\n{'─' * 35}\n\n"
                sent_pages += 1

        if full_text.strip():
            caption = f"📖 **شاهنامه فردوسی** — تصحیح جلال خالقی مطلق\n\n"
            caption += full_text
            caption += f"📍 فایل {current_file_idx + 1} از ۵\n"
            caption += f"📅 {datetime.now().strftime('%Y/%m/%d')}"

            # اگر متن خیلی طولانی بود، آن را به چند پیام تقسیم می‌کنیم
            if len(caption) > 4000:
                parts = [caption[i:i+4000] for i in range(0, len(caption), 4000)]
                for part in parts:
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        json={"chat_id": CHANNEL_ID, "text": part}
                    )
                print(f"✅ متن به {len(parts)} پیام تقسیم و ارسال شد")
            else:
                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    json={"chat_id": CHANNEL_ID, "text": caption}
                )
                if response.status_code == 200:
                    print(f"✅ {sent_pages} صفحه به صورت متن ارسال شد")
                else:
                    print("خطا در ارسال:", response.text)

            save_state(current_file_idx, current_page + sent_pages)
        else:
            print("هیچ متنی استخراج نشد.")

    except Exception as e:
        print(f"خطا: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("توکن یا CHANNEL_ID تنظیم نشده است")
    else:
        send_post()
