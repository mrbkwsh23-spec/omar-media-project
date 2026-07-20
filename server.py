import os
import re
import threading
import time
import requests
import yt_dlp
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8869258158:AAHQPSlAHl4Bqyx5o8Xi8G0Cf3uzxMaDvCo"

# دالة لفتح بورت ويب وإرسال نبضات ذاتية لإبقاء السيرفر مستيقظاً 24 ساعة للأبد
def run_dummy_server():
    class DummyHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Bot is Live and Anti-Sleep is Active!")
            
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    
    # خيط فرعي لإرسال طلب ذاتي كل 10 دقائق لتفادي نوم السيرفر المجاني
    def keep_alive_ping():
        time.sleep(30)
        while True:
            try:
                # نبضة تنشيط ذاتية للسيرفر ليبقى حياً دائماً
                requests.get(f"http://localhost:{port}", timeout=5)
            except Exception:
                pass
            time.sleep(600) # يكرر النبضة كل 10 دقائق
            
    threading.Thread(target=keep_alive_ping, daemon=True).start()
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"🎬 مرحباً بك يا {update.effective_user.first_name} في بوت صيد الميديا العالمي المطور! 🤖⚡\n\n"
        "البوت محصن الآن ضد حظر يوتيوب ويعمل بنظام البث المستمر بدون نوم 🌐.\n\n"
        "📥 لجلب ملفك فوراً وبدون تعليق، أرسل الأمر بالتنسيق التالي:\n"
        "🔹 لتحميل الفيديو اكتب: `/video رابط_الفيديو`\n"
        "🔹 لتحميل صوت MP3 اكتب: `/mp3 رابط_الفيديو`"
    )

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرابط بعد الأمر هكذا:\n`/video رابط_الفيديو`")
        return
    url = context.args[0]
    await update.message.reply_text("⏳ جاري سحب وتحميل الفيديو سحابياً بأعلى سرعة.. يرجى الانتظار ثوانٍ...")
    
    # تفعيل محاكاة بصمة المتصفح لتخطي حظر الـ Bot Detection في يوتيوب وتيك توك
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s_video.%(ext)s',
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
        'impersonate': 'chrome', # محاكاة متصفح كروم لإنسان حقيقي 🎯
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="🎬 تم تحميل الفيديو بنجاح عبر البوت السحابي المطور!")
        os.remove(filename)
    except Exception as e:
        await update.message.reply_text("❌ عذراً! الرابط محمي جداً أو هناك ضغط على خوادم المنصة حالياً، جرب لاحقاً بسلام.")

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
        'impersonate': 'chrome', # كسر حظر يوتيوب الصارم في استخراج الصوت 🎯
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename_mp3 = re.sub(r'\.[^.]+$', '.mp3', filename)
        with open(filename_mp3, 'rb') as audio:
            await update.message.reply_audio(audio=audio, caption="🎵 تم تحويل المقطع إلى MP3 بنجاح عبر البوت السحابي المطور!")
        os.remove(filename_mp3)
    except Exception as e:
        await update.message.reply_text("❌ فشل استخراج الـ MP3 بسبب حماية المنصة الصارمة الحين، جرب رابطاً آخر.")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("video", video_command))
    application.add_handler(CommandHandler("mp3", mp3_command))
    print("[+] بوت الصيد العالمي المحصن شغال الحين...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
