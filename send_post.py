import requests
import json
import os
from datetime import datetime
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

print("=== شاهنامه خالقی مطلق - استخراج متن (نسخه اصلاح‌شده) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAGES_PER_POST = 6

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
        json.dump({
            "current_file": current_file,
            "current_page": current_page
        }, f, ensure_ascii=False, indent=2)

def clean_text(text):
    """پاکسازی متن برای جلوگیری از ارور Markdown"""
    if not text:
        return ""
    # حذف کاراکترهای مشکل‌ساز Markdown
    text = text.replace('*', '∗').replace('_', 'ـ').replace('`', "'").replace('[', '［').replace(']', '］')
    text = text.replace('**', '').replace('__', '')
    return text.strip()

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
        images = convert_from_path(pdf_path, dpi=200, first_page=current_page + 1, 
                                 last_page=current_page + PAGES_PER_POST)

        full_text = ""
        sent_pages = 0

        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang='fas', config='--psm 6')
            cleaned = clean_text(text)
            if cleaned:
                full_text += f"**صفحه {current_page + i + 1}**\n\n{cleaned}\n\n{'─' * 30}\n\n"
                sent_pages += 1

        if full_text.strip():
            caption = f"📖 **شاهنامه فردوسی** (تصحیح جلال خالقی مطلق)\n\n"
            caption += full_text
            caption += f"\n📍 فایل {current_file_idx + 1} از ۵ | صفحات {current_page + 1} تا {current_page + sent_pages}"
            caption += f"\n📅 {datetime.now().strftime('%Y/%m/%d')}"

            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": CHANNEL_ID,
                    "text": caption,
                    "parse_mode": ""   # خالی گذاشتن = ارسال به صورت متن معمولی
                }
            )

            if response.status_code == 200:
                print(f"✅ {sent_pages} صفحه با موفقیت ارسال شد")
                save_state(current_file_idx, current_page + sent_pages)
            else:
                print("خطا در ارسال:", response.text)
        else:
            print("هیچ متنی استخراج نشد.")

    except Exception as e:
        print(f"خطا: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("توکن یا CHANNEL_ID تنظیم نشده است")
    else:
        send_post()
