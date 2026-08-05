import requests
import json
import os
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import tempfile

print("=== شاهنامه خالقی مطلق - ارسال عکس با کیفیت (نسخه نهایی) ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PAGES_PER_POST = 5

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

def add_header(image, page_number):
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        page_font = ImageFont.truetype("DejaVuSans.ttf", 38)
    except:
        title_font = ImageFont.load_default()
        page_font = ImageFont.load_default()

    # هدر مشکی با متن طلایی
    draw.rectangle([(0, 0), (image.width, 110)], fill=(15, 15, 15))
    draw.text((60, 18), "شاهنامه فردوسی", fill=(255, 215, 0), font=title_font)
    draw.text((60, 65), f"تصحیح جلال خالقی مطلق - صفحه {page_number}", fill=(220, 220, 220), font=page_font)
    
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

        media = []
        temp_files = []

        for i, pil_image in enumerate(images):
            page_num = current_page + i + 1
            processed = add_header(pil_image, page_num)
            
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            processed.save(tmp.name, 'JPEG', quality=95)
            media.append(tmp.name)
            temp_files.append(tmp.name)

        # ارسال به صورت آلبوم
        files = []
        for idx, img_path in enumerate(media):
            files.append(("media", open(img_path, "rb")))

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
            data={
                "chat_id": CHANNEL_ID,
                "caption": f"📖 شاهنامه فردوسی (تصحیح جلال خالقی مطلق)\n"
                          f"فایل {current_file_idx + 1} از ۵ | صفحات {current_page + 1} تا {current_page + len(images)}\n"
                          f"📅 {datetime.now().strftime('%Y/%m/%d')}",
                "parse_mode": "Markdown"
            },
            files=files
        )

        if response.status_code == 200:
            print(f"✅ موفقیت: {len(images)} صفحه ارسال شد")
            save_state(current_file_idx, current_page + len(images))
        else:
            print("خطا در ارسال:", response.text)

    except Exception as e:
        print(f"خطا: {e}")
    finally:
        for f in temp_files:
            try:
                os.unlink(f)
            except:
                pass

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("توکن یا CHANNEL_ID تنظیم نشده است")
    else:
        send_post()
