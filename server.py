import os
import re
import threading
import time
import requests
import yt_dlp
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8836632507:AAGe1mHJMBlRaLCUoveAJA_j700xUvxNWEQ"

# ذاكرة مؤقتة معزولة لحفظ الروابط بدقة
user_links = {}

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
    
    # 🔥 الخلطة السرية السحرية: إرسال نبضة تنشيط ذاتية كل 5 دقائق لمنع النوم نهائياً
    def keep_alive_pinger():
        time.sleep(20) # الانتظار لحين اكتمال إقلاع السيرفر
        while True:
            try:
                # السيرفر يتصل بنفسه داخلياً ليبقى مستيقظاً للأبد
                requests.get(f"http://localhost:{port}", timeout=5)
                print("[*] تم ضخ نبضة التنشيط الذاتية بنجاح.. السيرفر مستيقظ 24 ساعة!")
            except Exception:
                pass
            time.sleep(300) # يكرر الطلب تلقائياً كل 5 دقائق (300 ثانية)
            
    threading.Thread(target=keep_alive_pinger, daemon=True).start()
    server.serve_forever()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_links.clear() # تنظيف الذاكرة المؤقتة من الجلسات الميتة
    await update.message.reply_text(
        f"🎬 مرحباً بك يا {update.effective_user.first_name} في بوت صيد الميديا العالمي الخارق! 🤖⚡\n\n"
        "البوت محصن الآن ضد النوم ويعمل 24 ساعة بدون توقف من السحاب 🌐.\n\n"
        "📥 أرسل رابط الفيديو الحين هنا في الشات لتنبثق لك لوحة التنزيل الفورية:"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()
    chat_id = update.effective_chat.id
    
    if url.startswith("http://") or url.startswith("https://"):
        user_links[chat_id] = url
        
        # أزرار نيون فخمة وسريعة الاستجابة
        keyboard = [
            [InlineKeyboardButton("تحميل كـ فيديو عالي الجودة 🎬", callback_data='download_video')],
            [InlineKeyboardButton("تحويل وتحميل كـ صوت MP3 🎵", callback_data='download_mp3')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎯 تم التقاط الرابط بنجاح سحابياً!\n"
            "اختر الصيغة التي تبي تحميلها من الأزرار أدناه الحين:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("⚠️ يرجى إرسال رابط فيديو صحيح يبدأ بـ http أو https لكي يشتغل الصيد.")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    # قطع دائر الانتظار فوراً لمنع تجميد أو دوران أزرار التيليجرام اللعينة
    await query.answer()
    
    if chat_id not in user_links:
        await query.message.reply_text("⚠️ انتهت صلاحية الجلسة، يرجى إرسال الرابط مجدداً بسلام.")
        return
        
    url = user_links[chat_id]
    
    if query.data == 'download_video':
        status_msg = await query.message.reply_text("⏳ جاري سحب وتحميل الفيديو سحابياً بأعلى سرعة.. يرجى الانتظار ثوانٍ...")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s_video.%(ext)s',
            'restrictfilenames': True,
            'quiet': True,
            'no_warnings': True,
            'impersonate': 'chrome', # كسر الحظر بمحاكاة متصفح حقيقي 🎯
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            with open(filename, 'rb') as video:
                await query.message.reply_video(video=video, caption="🎬 تم صيد وتحميل الفيديو بنجاح عبر بوت عُمر السحابي!")
            os.remove(filename)
            await status_msg.delete()
        except Exception:
            await status_msg.edit_text("❌ عذراً! الرابط محمي جداً أو المنصة فرضت حظراً مؤقتاً، جرب رابطاً آخر بسلام.")
            
    elif query.data == 'download_mp3':
        status_msg = await query.message.reply_text("⏳ جاري استخراج الصوت وتحويله إلى MP3 ناصع النقاء سحابياً الحين...")
        
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
                await query.message.reply_audio(audio=audio, caption="🎵 تم تحويل المقطع إلى MP3 بنجاح عبر بوت عُمر السحابي!")
            os.remove(filename_mp3)
            await status_msg.delete()
        except Exception:
            await status_msg.edit_text("❌ فشل استخراج الـ MP3 بسبب قيود الحماية الصارمة للمنصة حالياً.")
            
    if chat_id in user_links:
        del user_links[chat_id]

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    print("[+] بوت صيد الميديا السحابي المستيقظ شغال الحين بكفاءة عظمى...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()

