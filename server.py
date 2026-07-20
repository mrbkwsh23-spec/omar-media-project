import os
import re
import asyncio
import yt_dlp
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8836632507:AAGe1mHJMBlRaLCUoveAJA_j700xUvxNWEQ"
RENDER_EXTERNAL_URL = "https://omar-media-project.onrender.com"

app = Flask(__name__)

# بناء التطبيق وتهيئته للعمل الفوري
application = Application.builder().token(TOKEN).build()

@app.route('/')
def home():
    return "السيرفر مستقر ويعمل بنجاح! 🚀"

@app.route(f'/{TOKEN}', methods=['POST'])
def telegram_webhook():
    if request.method == "POST":
        try:
            # قراءة التحديث القادم من تليجرام
            update_data = request.get_json(force=True)
            update = Update.de_json(update_data, application.bot)
            
            # الطريقة الصحيحة والمضمونة لإجبار تليجرام على معالجة الرد وإرساله للشات فوراً
            asyncio.run_coroutine_threadsafe(application.process_update(update), application.loop)
        except Exception as e:
            print(f"Error processing update: {e}")
            
    return "OK", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"🎬 مرحباً بك يا {update.effective_user.first_name} في بوت صيد الميديا المحصن! 🤖⚡\n\n"
        "📥 لجلب ملفك فوراً وبدون تعليق، أرسل الأمر بالتنسيق التالي في الشات الحين:\n"
        "🔹 لتحميل الفيديو اكتب: `/video رابط_الفيديو`\n"
        "🔹 لتحميل صوت MP3 اكتب: `/mp3 رابط_الفيديو`"
    )

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرابط بعد الأمر هكذا:\n`/video رابط_الفيديو`")
        return
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ جاري سحب وتحميل الفيديو سحابياً.. يرجى الانتظار ثوانٍ...")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': 'downloads/%(id)s_video.%(ext)s',
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="🎬 تم تحميل الفيديو بنجاح عبر بوت عُمر السحابي!")
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        await update.message.reply_text("❌ عذراً! الرابط غير مدعوم حالياً أو محمي.")
    finally:
        try: await status_msg.delete()
        except: pass

async def mp3_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرابط بعد الأمر هكذا:\n`/mp3 رابط_الفيديو`")
        return
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ جاري استخراج وتجهيز ملف الـ MP3 ناصع النقاء الحين...")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(id)s_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename_mp3 = re.sub(r'\.[^.]+$', '.mp3', filename)
        with open(filename_mp3, 'rb') as audio:
            await update.message.reply_audio(audio=audio, caption="🎵 تم تحويل المقطع إلى MP3 بنجاح عبر بوت عُمر السحابي!")
        if os.path.exists(filename_mp3):
            os.remove(filename_mp3)
    except Exception as e:
        await update.message.reply_text("❌ فشل استخراج الـ MP3.")
    finally:
        try: await status_msg.delete()
        except: pass

# إضافة الأوامر للبوت
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("video", video_command))
application.add_handler(CommandHandler("mp3", mp3_command))

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    # تهيئة حلقة الأحداث الأساسية للتطبيق بشكل مسبق لضمان عمل الروبوت في الخلفية
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}"))
    application.loop = loop
    
    print(f"[+] Webhook successfully linked to {RENDER_EXTERNAL_URL}")
    
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
