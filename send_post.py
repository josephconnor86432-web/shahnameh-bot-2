import requests
import json
import os
import time
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import tempfile

print("=== شاهنامه خالقی مطلق - ارسال عکس با تأخیر ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAGES_PER_POST = 5           # تعداد صفحه در هر پست
DELAY_BETWEEN_PHOTOS = 5     # تأخیر به ثانیه بین هر عکس

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
                return data.get("current_file", 0), data.get("current_page", 36)  # شروع از صفحه ۳۷
        except:
            return 0, 36
    return 0, 36

def save_state(current_file, current_page):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({"current_file": current_file, "current_page": current_page}, f, ensure_ascii=False, indent=2)

def add_header(image, page_number):
    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 50)
        font_page = ImageFont.truetype("DejaVuSans.ttf", 38)
    except:
        font_title = ImageFont.load_default()
        font_page = ImageFont.load_default()

    draw.rectangle([(0, 0), (image.width, 140)], fill=(8, 8, 28))
    draw.text((80, 25), "شاهنامه فردوسی", fill=(255, 215, 0), font=font_title)
    draw.text((80, 82), f"تصحیح جلال خالقی مطلق • صفحه {page_number}", fill=(220, 220, 220), font=font_page)
    return image

def send_post():
    current_file_idx, current_page = load_state()
    
    if current_file_idx >= len(PDF_FILES):
        print("تمام فایل‌ها ارسال شدند.")
        return

    pdf_path = PDF_FILES[current_file_idx]
    if not os.path.exists(pdf_path):
        print(f"فایل پیدا نشد: {pdf_path}")
        return

    print(f"ارسال صفحات {current_page + 1} تا {current_page + PAGES_PER_POST} (فایل {current_file_idx + 1}/5)")

    try:
        images = convert_from_path(pdf_path, dpi=220, first_page=current_page + 1, 
                                 last_page=current_page + PAGES_PER_POST)

        for i, pil_image in enumerate(images):
            page_num = current_page + i + 1
            processed = add_header(pil_image, page_num)
            
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                processed.save(tmp.name, 'JPEG', quality=93)
                temp_path = tmp.name

            caption = f"📖 شاهنامه فردوسی (تصحیح جلال خالقی مطلق)\nصفحه {page_num}\n\n📅 {datetime.now().strftime('%Y/%m/%d')}"

            with open(temp_path, 'rb') as photo:
                response = requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                    data={
                        "chat_id": CHANNEL_ID,
                        "caption": caption,
                        "parse_mode": "Markdown"
                    },
                    files={"photo": photo}
                )

            os.unlink(temp_path)

            if response.status_code == 200:
                print(f"✅ صفحه {page_num} ارسال شد")
            else:
                print(f"خطا در ارسال صفحه {page_num}:", response.text)

            time.sleep(DELAY_BETWEEN_PHOTOS)  # تأخیر ۵ ثانیه بین هر عکس

        save_state(current_file_idx, current_page + len(images))

    except Exception as e:
        print(f"خطا: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("توکن یا CHANNEL_ID تنظیم نشده است")
    else:
        send_post()
