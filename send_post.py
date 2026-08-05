import requests
import json
import os
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import tempfile

print("=== شاهنامه خالقی مطلق - ارسال عکس (نسخه اصلاح شده) ===")

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
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
        font_page = ImageFont.truetype("DejaVuSans.ttf", 36)
    except:
        font_title = ImageFont.load_default()
        font_page = ImageFont.load_default()

    draw.rectangle([(0, 0), (image.width, 130)], fill=(10, 10, 30))
    draw.text((70, 25), "شاهنامه فردوسی", fill=(255, 215, 0), font=font_title)
    draw.text((70, 78), f"تصحیح جلال خالقی مطلق • صفحه {page_number}", fill=(200, 200, 200), font=font_page)
    return image

def send_post():
    current_file_idx, current_page = load_state()
    
    if current_file_idx >= len(PDF_FILES):
        print("تمام فایل‌ها ارسال شده‌اند.")
        return

    pdf_path = PDF_FILES[current_file_idx]
    if not os.path.exists(pdf_path):
        print(f"فایل پیدا نشد: {pdf_path}")
        return

    print(f"ارسال صفحات {current_page + 1} تا {current_page + PAGES_PER_POST} (فایل {current_file_idx + 1}/5)")

    try:
        images = convert_from_path(pdf_path, dpi=220, first_page=current_page + 1, 
                                 last_page=current_page + PAGES_PER_POST)

        media_array = []
        files = {}
        temp_files = []

        for i, pil_image in enumerate(images):
            page_num = current_page + i + 1
            processed_image = add_header(pil_image, page_num)
            
            tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            processed_image.save(tmp_file.name, 'JPEG', quality=92)
            temp_files.append(tmp_file.name)
            
            file_key = f"file{i}"
            media_array.append({
                "type": "photo",
                "media": f"attach://{file_key}"
            })
            files[file_key] = open(tmp_file.name, 'rb')

        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup",
            data={
                "chat_id": CHANNEL_ID,
                "media": json.dumps(media_array),
                "caption": f"📖 شاهنامه فردوسی (تصحیح جلال خالقی مطلق)\n"
                          f"فایل {current_file_idx + 1} از ۵ — صفحات {current_page + 1} تا {current_page + len(images)}\n"
                          f"📅 {datetime.now().strftime('%Y/%m/%d')}",
                "parse_mode": "Markdown"
            },
            files=files
        )

        if response.status_code == 200:
            print(f"✅ موفقیت: {len(images)} صفحه به صورت آلبوم ارسال شد")
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
