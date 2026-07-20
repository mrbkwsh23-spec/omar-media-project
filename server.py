import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8836632507:AAGe1mHJMBlRaLCUoveAJA_j700xUvxNWEQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"🎬 مرحباً يا {update.effective_user.first_name} في بوت صيد الميديا المحصن!\n\n"
        "📥 أرسل الأمر بالشكل التالي:\n"
        "🔹 `/video رابط_الفيديو`\n"
        "🔹 `/mp3 رابط_الفيديو`\n\n"
        "✅ يدعم: YouTube, TikTok, Instagram, Twitter/X, Facebook ومعظم المنصات"
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE, is_video: bool):
    if not context.args:
        await update.message.reply_text("⚠️ يرجى إرفاق الرابط بعد الأمر")
        return

    url = context.args[0].strip()
    status_msg = await update.message.reply_text("⏳ جاري التحميل...")

    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s_%(title)s.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extractor_retries': 5,
            'socket_timeout': 60,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36',
            },
        }

        if is_video:
            ydl_opts['format'] = 'best[height<=720]/best'
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not is_video:
                filename = re.sub(r'\.[^.]+$', '.mp3', filename)

        if not os.path.exists(filename):
            await status_msg.edit_text("❌ لم يتم العثور على الملف")
            return

        with open(filename, 'rb') as f:
            if is_video:
                await update.message.reply_video(
                    video=f,
                    caption="✅ تم التحميل بنجاح!",
                    supports_streaming=True
                )
            else:
                await update.message.reply_audio(
                    audio=f,
                    caption="✅ تم تحويله إلى MP3 بنجاح!"
                )

        os.remove(filename)
        await status_msg.delete()

    except Exception as e:
        error_str = str(e).lower()
        if "sign in" in error_str or "confirm" in error_str:
            err_msg = "❌ يوتيوب يحتاج تحديث (جرب رابط آخر)"
        elif "private" in error_str or "unavailable" in error_str:
            err_msg = "❌ الفيديو خاص أو غير متاح"
        else:
            err_msg = f"❌ خطأ: {str(e)[:120]}"
        await status_msg.edit_text(err_msg)

def main():
    os.makedirs('downloads', exist_ok=True)
    
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("video", lambda u, c: download_media(u, c, True)))
    application.add_handler(CommandHandler("mp3", lambda u, c: download_media(u, c, False)))
    
    print("[+] ✅ البوت شغال 24/7 - يدعم جميع المنصات")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
