import requests
import json
import os
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import tempfile

print("=== شاهنامه به نثر پارسی سره - ارسال ۱۰ صفحه روزانه ===")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PDF_FILENAME = "شاهنامه_به_نثر_پارسی_سره_از_میترا.pdf"
PAGES_PER_POST = 10

def load_state():
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r", encoding="utf-8") as f:
                return json.load(f).get("last_page", 0)
        except:
            return 0
    return 0

def save_state(last_page):
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump({"last_page": last_page}, f, ensure_ascii=False, indent=2)

def add_page_number(img, page_num, total_pages):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    text = f"صفحه {page_num} از {total_pages} • شاهنامه به نثر پارسی سره"
    draw.text((30, 30), text, fill=(0, 0, 0), font=font)
    return img

def send_post():
    if not os.path.exists(PDF_FILENAME):
        print(f"❌ فایل {PDF_FILENAME} پیدا نشد!")
        return

    last_page = load_state()
    total_pages = len(convert_from_path(PDF_FILENAME, dpi=150, first_page=1, last_page=1)) * 10  # تخمینی

    print(f"ارسال صفحات {last_page + 1} تا {last_page + PAGES_PER_POST}")

    images = []
    temp_files = []

    try:
        pages = convert_from_path(
            PDF_FILENAME,
            dpi=200,
            first_page=last_page + 1,
            last_page=last_page + PAGES_PER_POST,
            thread_count=2
        )

        for i, page in enumerate(pages, 1):
            current_page = last_page + i
            page_with_number = add_page_number(page, current_page, total_pages)
            
            tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            page_with_number.save(tmp_file.name, 'JPEG', quality=85)
            images.append(tmp_file.name)
            temp_files.append(tmp_file.name)

        # ارسال به صورت آلبوم (Media Group)
        media = []
        for img_path in images:
            media.append({
                "type": "photo",
                "media": open(img_path, "rb")
            })

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMediaGroup"
        payload = {
            "chat_id": CHANNEL_ID,
            "caption": f"📖 **شاهنامه به نثر پارسی سره**\n\n"
                       f"صفحات {last_page + 1} تا {last_page + len(pages)}\n"
                       f"📅 {datetime.now().strftime('%Y/%m/%d')}",
            "parse_mode": "Markdown"
        }

        files = [("media", (f"page{i}.jpg", open(img, "rb"), "image/jpeg")) for i, img in enumerate(images)]

        response = requests.post(url, data=payload, files=files)

        if response.status_code == 200:
            print(f"✅ موفقیت: {len(pages)} صفحه ارسال شد")
            save_state(last_page + len(pages))
        else:
            print("❌ خطا در ارسال:", response.text)

    except Exception as e:
        print(f"خطا: {e}")
    finally:
        # پاک کردن فایل‌های موقت
        for f in temp_files:
            try:
                os.unlink(f)
            except:
                pass

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
