import os
import asyncio
import uuid
import logging
import subprocess
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import yt_dlp

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Havolalarni vaqtincha saqlash uchun lug'at (tezkor xotira)
url_cache = {}

def extract_audio_fast(video_path, audio_path):
    # Videodan audioni qayta yuklamasdan juda tez ajratib olish (ffmpeg)
    cmd = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", audio_path, "-y"]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def download_media(url: str, mode: str, unique_id: str):
    base_name = f"media_{unique_id}"
    
    # Maksimal tezlik uchun yt-dlp sozlamalari
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
    }
    
    if mode == 'audio':
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['outtmpl'] = f"{base_name}"
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return None, f"{base_name}.mp3"
    
    else: # video uchun
        ydl_opts['format'] = 'best'
        ydl_opts['outtmpl'] = f"{base_name}.mp4"
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Fayl nomini aniqlash
        video_file = None
        for file in os.listdir('.'):
            if file.startswith(base_name) and not file.endswith('.mp3'):
                video_file = file
                break
        
        return video_file, None

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("👋 Assalomu alaykum!\nInstagram Reels havolasini yuboring.")

@dp.message(F.text.contains("instagram.com"))
async def ask_format_handler(message: types.Message):
    url = message.text.strip()
    
    # 3 ta tugmani yaratamiz
    builder = InlineKeyboardBuilder()
    builder.button(text="🎬 Video", callback_data="dl_video")
    builder.button(text="🎵 Audio", callback_data="dl_audio")
    builder.button(text="🎬+🎵 Ikkalasi", callback_data="dl_both")
    builder.adjust(2, 1) # Tepada 2 ta, pastda 1 ta tugma
    
    sent_msg = await message.reply("Nimani yuklab olmoqchisiz? Tanlang 👇", reply_markup=builder.as_markup())
    
    # Linkni bosilgan tugmaga bog'lash uchun xotirada saqlaymiz
    url_cache[sent_msg.message_id] = url

@dp.callback_query(F.data.startswith("dl_"))
async def process_download(callback: types.CallbackQuery):
    choice = callback.data.split("_")[1] # 'video', 'audio', yoki 'both'
    msg_id = callback.message.message_id
    
    url = url_cache.get(msg_id)
    if not url:
        await callback.answer("Havola eskirgan, iltimos linkni qaytadan yuboring.", show_alert=True)
        return
        
    await callback.message.edit_text("⚡️ Yuklanmoqda... Iltimos, kuting.")
    unique_id = str(uuid.uuid4())[:8]
    
    try:
        if choice == "audio":
            _, audio_file = await asyncio.to_thread(download_media, url, 'audio', unique_id)
            if audio_file and os.path.exists(audio_file):
                await callback.message.answer_audio(FSInputFile(audio_file), caption="🎵 Reels audiosi")
                os.remove(audio_file)
                
        elif choice == "video":
            video_file, _ = await asyncio.to_thread(download_media, url, 'video', unique_id)
            if video_file and os.path.exists(video_file):
                await callback.message.answer_video(FSInputFile(video_file), caption="🎬 Reels videosi")
                os.remove(video_file)
                
        elif choice == "both":
            # Ikkalasini bosganda 2 marta yuklab o'tirmaymiz.
            # Videoni olib, undan soniya ichida audioni ajratamiz (Super tezlik)
            video_file, _ = await asyncio.to_thread(download_media, url, 'video', unique_id)
            if video_file and os.path.exists(video_file):
                audio_file = f"media_{unique_id}.mp3"
                await asyncio.to_thread(extract_audio_fast, video_file, audio_file)
                
                # Ikkalasini ham yuboramiz
                await callback.message.answer_video(FSInputFile(video_file), caption="🎬 Reels videosi")
                if os.path.exists(audio_file):
                    await callback.message.answer_audio(FSInputFile(audio_file), caption="🎵 Reels audiosi")
                    os.remove(audio_file)
                os.remove(video_file)

        # Ish bitgach "Yuklanmoqda..." degan xabarni o'chirib yuboramiz
        await callback.message.delete()
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await callback.message.edit_text("⚠️ Xatolik yuz berdi. Instagram vaqtincha cheklov qo'ygan bo'lishi mumkin.")
        
    finally:
        # Keshni tozalash
        url_cache.pop(msg_id, None)

async def main():
    print("🚀 Maksimal tezlashtirilgan va menyuli bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())