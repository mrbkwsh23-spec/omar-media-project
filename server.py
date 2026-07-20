
import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8836632507:AAGe1mHJMBlRaLCUoveAJA_j700xUvxNWEQ"

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
    await update.message.reply_text("⏳ جاري سحب وتحميل الفيديو سحابياً بأعلى سرعة.. يرجى الانتظار ثوانٍ...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s_video.%(ext)s',
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="🎬 تم تحميل الفيديو بنجاح عبر بوت عُمر السحابي!")
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text("❌ عذراً! الرابط محمي أو غير مدعوم حالياً في السيرفر، جرب رابطاً آخر بسلام.")

async def mp3_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرابط بعد الأمر هكذا:\n`/mp3 رابط_الفيديو`")
        return
    url = context.args[0]
    await update.message.reply_text("⏳ جاري استخراج وتجهيز ملف الـ MP3 ناصع النقاء سحابياً الحين...")
    
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
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename_mp3 = re.sub(r'\.[^.]+$', '.mp3', filename)
        with open(filename_mp3, 'rb') as audio:
            await update.message.reply_audio(audio=audio, caption="🎵 تم تحويل المقطع إلى MP3 بنجاح عبر بوت عُمر السحابي!")
        os.remove(filename_mp3)
    except Exception as e:
        await update.message.reply_text("❌ فشل استخراج الـ MP3 بسبب حماية المنصة، جرب رابط يوتيوب أو فيسبوك عام.")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("video", video_command))
    application.add_handler(CommandHandler("mp3", mp3_command))
    print("[+] بوت الصيد الفوري المطور شغال الحين...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()


