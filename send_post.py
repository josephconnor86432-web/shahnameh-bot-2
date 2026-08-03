import requests
import json
import os
from datetime import datetime
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import tempfile

print("=== شاهنامه به نثر پارسی سره - نسخه پایدار (۱۰ صفحه روزانه) ===")

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

def add_page_number(img, page_num):
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 42)
    except:
        font = ImageFont.load_default()
    
    text = f"صفحه {page_num} • شاهنامه به نثر پارسی سره از میترا"
    draw.text((40, 30), text, fill=(0, 0, 0), font=font)
    return img

def send_post():
    if not os.path.exists(PDF_FILENAME):
        print(f"❌ فایل PDF پیدا نشد: {PDF_FILENAME}")
        return

    last_page = load_state()
    print(f"در حال ارسال صفحات {last_page + 1} تا {last_page + PAGES_PER_POST}")

    try:
        pages = convert_from_path(
            PDF_FILENAME,
            dpi=180,
            first_page=last_page + 1,
            last_page=last_page + PAGES_PER_POST,
            thread_count=2
        )

        sent_count = 0
        for i, page_img in enumerate(pages):
            current_page = last_page + i + 1
            
            # اضافه کردن شماره صفحه
            page_with_text = add_page_number(page_img, current_page)
            
            # ذخیره موقت
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                page_with_text.save(tmp.name, 'JPEG', quality=90)
                temp_path = tmp.name

            # ارسال تک تک (پایدارتر)
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            caption = f"📖 صفحه {current_page}\n\n" \
                     f"شاهنامه به نثر پارسی سره از میترا\n" \
                     f"📅 {datetime.now().strftime('%Y/%m/%d')}"

            with open(temp_path, 'rb') as photo:
                response = requests.post(
                    url,
                    data={
                        "chat_id": CHANNEL_ID,
                        "caption": caption,
                        "parse_mode": "Markdown"
                    },
                    files={"photo": photo}
                )

            os.unlink(temp_path)  # پاک کردن فایل موقت

            if response.status_code == 200:
                sent_count += 1
                print(f"✅ صفحه {current_page} ارسال شد")
            else:
                print(f"❌ خطا در ارسال صفحه {current_page}: {response.text}")
                break

        if sent_count > 0:
            save_state(last_page + sent_count)
            print(f"✅ مجموع {sent_count} صفحه با موفقیت ارسال شد")
        else:
            print("❌ هیچ صفحه‌ای ارسال نشد")

    except Exception as e:
        print(f"خطای کلی: {e}")

if __name__ == "__main__":
    if not BOT_TOKEN or not CHANNEL_ID:
        print("❌ توکن یا آیدی کانال تنظیم نشده است")
    else:
        send_post()
