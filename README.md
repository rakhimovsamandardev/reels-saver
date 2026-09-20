
# 📥 Instagram Reels Downloader Bot

Bu Telegram bot Instagram Reels havolalarini qabul qilib, ulardan **Video**, **Audio (MP3)** yoki **Ikkalasini birgalikda** juda tez yuklab berish imkoniyatiga ega. 

Loyiha **Aiogram 3**, **yt-dlp** va **FFmpeg** yordamida maksimal darajada optimizatsiya qilingan.

## 🚀 Asosiy imkoniyatlar

- **Uch xil yuklash rejimi:** Video (MP4), Audio (MP3), yoki ikkalasi birga.
- **Tezkor audio ajratish:** "Ikkalasi" tanlanganda, bot internetdan ikki marta ma'lumot yuklamaydi. Videoni olib, uning ichidan `ffmpeg` orqali soniya ichida audioni ajratib oladi.
- **Xavfsizlik:** Bot tokeni va maxfiy ma'lumotlar `.env` faylida xavfsiz saqlanadi.
- **Avtomatik tozalash:** Yuborilgan fayllar server (yoki kompyuter) xotirasini to'ldirmasligi uchun darhol o'chiriladi.

## ⚙️ Talablar (Prerequisites)

Ushbu bot ishlashi uchun kompyuteringiz yoki serveringizda quyidagilar o'rnatilgan bo'lishi shart:
1. **Python 3.8** yoki undan yuqori versiya.
2. **FFmpeg** (Videodan audioni qirqib olish uchun kerak).

*FFmpeg o'rnatilganini tekshirish uchun terminalda yozing:*
```bash
ffmpeg -version
