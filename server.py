import os
import re
import yt_dlp
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

TOKEN = "8836632507:AAGe1mHJMBlRaLCUoveAJA_j700xUvxNWEQ"

app = Flask(__name__)
bot = Bot(token=TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎬 مرحباً يا {update.effective_user.first_name}!\n\n"
        "🔹 `/video رابط`\n"
        "🔹 `/mp3 رابط`\n\n"
        "✅ يدعم **كل** المنصات: YouTube, TikTok, Instagram, Facebook, Twitter/X, وغيرها"
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE, is_video: bool):
    if not context.args:
        await update.message.reply_text("⚠️ أرسل الرابط بعد الأمر")
        return

    url = context.args[0].strip()
    status = await update.message.reply_text("⏳ جاري التحميل من المنصة...")

    try:
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s_%(title)s.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,
            'noplaylist': True,
            'extractor_retries': 5,
            'socket_timeout': 60,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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

        with open(filename, 'rb') as f:
            if is_video:
                await update.message.reply_video(video=f, caption="✅ تم التحميل بنجاح!")
            else:
                await update.message.reply_audio(audio=f, caption="✅ تم تحويله إلى MP3!")

        os.remove(filename)
        await status.delete()

    except Exception as e:
        err = str(e).lower()
        if "facebook" in err or "instagram" in err or "private" in err:
            msg = "❌ هذا المحتوى قد يكون خاص أو محمي"
        else:
            msg = f"❌ خطأ: {str(e)[:100]}"
        await status.edit_text(msg)

# Setup
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("video", lambda u,c: download_media(u,c,True)))
application.add_handler(CommandHandler("mp3", lambda u,c: download_media(u,c,False)))

@app.route('/', methods=['GET'])
def home():
    return "✅ البوت شغال - يدعم كل المنصات"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    asyncio.run(application.process_update(update))
    return 'ok', 200

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    print("[+] ✅ البوت شغال 24/7 - دعم كامل لجميع المنصات")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
