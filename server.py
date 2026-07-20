import os
import re
import threading
import time
import requests
import yt_dlp
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 🔑 توكن بوتك OmarAiRobot_bot المفتوح في شاشتك حالياً الحين
TOKEN = "8869258158:AAHQPSlAHl4Bqyx5o8Xi8G0Cf3uzxMaDvCo"

# 🛰️ محرك ويب مدمج لفتح بورت الاتصال وضخ نبضات منع النوم التلقائي
def run_dummy_server():
    class DummyHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Omar Media Bot is Active, Live and Anti-Sleep Mode is Running 24/7!")
            
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    
    def keep_alive_pinger():
        time.sleep(20)
        while True:
            try:
                requests.get(f"http://localhost:{port}", timeout=5)
            except Exception:
                pass
            time.sleep(300) # نبضة تنشيط ذاتية كل 5 دقائق ليبقى حياً دائماً
            
    threading.Thread(target=keep_alive_pinger, daemon=True).start()
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"🎬 مرحباً بك يا {update.effective_user.first_name} في بوت صيد الميديا الفوري! 🤖⚡\n\n"
        "البوت يعمل الآن بنظام السرعة السحابية المباشرة والخالية من الأزرار والتعليق 🌐.\n\n"
        "📥 لجلب ملفك فوراً وبدون أي تعليق، أرسل الأمر بالتنسيق التالي في الشات الحين:\n"
        "🔹 لتحميل الفيديو اكتب: `/video رابط_الفيديو`\n"
        "🔹 لتحميل صوت MP3 اكتب: `/mp3 رابط_الفيديو`"
    )

async def video_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرابط بعد الأمر هكذا:\n`/video رابط_الفيديو`")
        return
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ جاري سحب وتحميل الفيديو سحابياً بأعلى سرعة.. يرجى الانتظار ثوانٍ...")
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(id)s_video.%(ext)s',
        'restrictfilenames': True,
        'quiet': True,
        'no_warnings': True,
        'impersonate': 'chrome', # محاكاة متصفح حقيقي لكسر الحظر 🎯
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video, caption="🎬 تم تحميل الفيديو بنجاح عبر بوت عُمر السحابي!")
        os.remove(filename)
        await status_msg.delete()
    except Exception:
        await status_msg.edit_text("❌ عذراً! الرابط محمي جداً أو غير مدعوم حالياً، جرب رابطاً آخر بسلام.")

async def mp3_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("⚠️ يرجى كتابة الرابط بعد الأمر هكذا:\n`/mp3 رابط_الفيديو`")
        return
    url = context.args[0]
    status_msg = await update.message.reply_text("⏳ جاري استخراج وتجهيز ملف الـ MP3 ناصع النقاء سحابياً الحين...")
    
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
        'impersonate': 'chrome', # كسر حظر يوتيوب وتيك توك الصارم 🎯
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            filename_mp3 = re.sub(r'\.[^.]+$', '.mp3', filename)
        with open(filename_mp3, 'rb') as audio:
            await update.message.reply_audio(audio=audio, caption="🎵 تم تحويل المقطع إلى MP3 بنجاح عبر بوت عُمر السحابي!")
        os.remove(filename_mp3)
        await status_msg.delete()
    except Exception:
        await status_msg.edit_text("❌ فشل استخراج الـ MP3 بسبب قيود الحماية الصارمة للمنصة حالياً.")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("video", video_command))
    application.add_handler(CommandHandler("mp3", mp3_command))
    
    print("[+] بوت صيد الميديا السحابي المستيقظ شغال الحين بكفاءة عظمى...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
