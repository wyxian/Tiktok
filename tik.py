
import os
import requests
import re
import time
import urllib.parse
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

API_ID = 21667552
API_HASH = "2d61c4dabe221927761e7770c76ba7bf"
BOT_TOKEN = "8182157193:AAH1VNIeq3lvWDPnd2z7vwhbdPTsTeukB5E"
ADMIN_ID = 5993632128
USER_DB = "users.txt"

app = Client("tiktok_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
}

def save_user(user_id):
    if not os.path.exists(USER_DB):
        open(USER_DB, 'w').close()
    with open(USER_DB, 'a+') as f:
        f.seek(0)
        users = f.read().splitlines()
        if str(user_id) not in users:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(USER_DB):
        return []
    with open(USER_DB, 'r') as f:
        return f.read().splitlines()

def extract_tiktok_url(text):
    pattern = r'https?://(?:www\.|vm\.|vt\.)?tiktok\.com/(?:@[\w\.-]+/video/\d+|[\w]+)'
    match = re.search(pattern, text)
    return match.group(0) if match else None

def resolve_tiktok_url(short_url):
    try:
        session = requests.Session()
        response = session.head(short_url, allow_redirects=True, timeout=10)
        return response.url
    except Exception as e:
        print(f"Resolve URL error: {e}")
        return None

def get_tiktok_video(url):
    try:
        encoded_url = urllib.parse.quote_plus(url)
        api_url = f"https://tikwm.com/api/?url={encoded_url}"
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        data = response.json()
        if data.get("data") and data["data"].get("play"):
            return data["data"]["play"]
    except Exception as e:
        print(f"API Error (tikwm): {e}")
    return None

@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    save_user(user.id)
    username = f"@{user.username}" if user.username else user.first_name
    welcome_text = (
        f"**မင်္ဂလာပါ {username}! \n\n"


        "TikTok Downloader Bot မှကြိုဆိုပါတယ်!**"
        "TikTok ဗီဒီယိုများကို ဒေါင်းလုဒ်ရယူရန် လင့်ခ်များပေးပို့ပါ။"
        "အခမဲ့အသုံးပြုနိုင်ပါသည်။"
    )
    await message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("ဖန်တီးသူ", url="https://t.me/wayxian")],
            [InlineKeyboardButton("အကူအညီ", callback_data="help")]
        ])
    )

@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply_text(
        "အသုံးပြုနည်း\n\n"
        "1. TikTok ဗီဒီယိုလင့်ခ်ကို ပေးပို့ပါ\n"
        "2. Bot မှ ဗီဒီယိုကို ဒေါင်းလုဒ်ဆွဲပေးပါမည်\n"
        "3. ဒေါင်းလုဒ်ပြီးသားဗီဒီယိုကို ရယူပါ\n\n"
        "ပြဿနာတစ်စုံတစ်ရာရှိပါက /report ကိုနှိပ်ပါ"
    )

@app.on_message(filters.command("users") & filters.user(ADMIN_ID))
async def list_users(client, message):
    users = get_users()
    count = len(users)
    await message.reply_text(f"စုစုပေါင်းအသုံးပြုသူများ: {count}\n\n" + "\n".join(users[:100]))

@app.on_message(filters.regex(r'https?://(?:www\.|vm\.|vt\.)?tiktok\.com/(?:@[\w\.-]+/video/\d+|[\w]+)'))
async def download_tiktok(client, message):
    try:
        url = extract_tiktok_url(message.text)
        if not url:
            await message.reply_text("❌ TikTok လင့်ခ်ကို ရှာမတွေ့ပါ")
            return

        resolved_url = resolve_tiktok_url(url)
        if resolved_url:
            url = resolved_url

        loading_msg = await message.reply_text("ဗီဒီယို ဒေါင်းလုဒ်ဆွဲနေပါသည်...")

        video_url = get_tiktok_video(url)
        if not video_url:
            await loading_msg.edit_text("❌ ဗီဒီယို ဒေါင်းလုဒ်ဆွဲ၍မရပါ (API ပြဿနာ)")
            return

        temp_file = f"temp_video_{int(time.time())}.mp4"
        with open(temp_file, 'wb') as f:
            response = requests.get(video_url, stream=True)
            for chunk in response.iter_content(chunk_size=1024*1024):
                f.write(chunk)

        await message.reply_video(video=temp_file, caption="✅ ဒေါင်းလုဒ်ပြီးပါပြီ!", supports_streaming=True)
        os.remove(temp_file)
        await loading_msg.delete()

    except Exception as e:
        print(f"Error: {e}")
        await message.reply_text("⚠️ အမှားတစ်ခု ဖြစ်ပေါ်နေပါသည်။")

print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
app.run()
