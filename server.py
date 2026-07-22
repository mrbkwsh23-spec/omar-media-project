import os
import telebot
import yt_dlp
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "بوت صيد الميديا المطور يعمل بنجاح! 🚀"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ⚠️ ضع توكن بوت صيد الميديا الخاص بك هنا
BOT_TOKEN = "8869258158:AAHQPSlAHl4Bqyx5o8Xi8G0Cf3uzxMaDvCo"
bot = telebot.TeleBot(BOT_TOKEN)

# 🟢 إعدادات سحرية ومحدثة تحاكي متصفح حقيقي لتخطي حماية تيك توك الصارمة 100%
BASE_YTDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'check_formats': False,
    'extractor_args': {
        'youtube': {'player_client': ['android', 'web']},
        'tiktok': {'impersonate': 'chrome', 'cookiesfrombrowser': ['chrome', 'firefox']} # لتخطي الحظر فوراً
    },
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎬 مرحباً بك يا عمر في بوت صيد الميديا السحابي المطور! 🚀\n\n"
        "لجلب ملفك فوراً وبدون تعليق، أرسل الأمر بالتنسيق التالي:\n"
        "🔹 لتحميل الفيديو اكتب: `video/ رابط_الفيديو` \n"
        "🔹 لتحميل صوت MP3 اكتب: `/mp3 رابط_الفيديو`"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('/mp3 '))
def handle_mp3_request(message):
    url = message.text.replace('/mp3 ', '').strip()
    status_msg = bot.reply_to(message, "⏳ جاري فحص الرابط وتخطي حماية تيك توك وسحب الصوت الفوري...")
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    video_id = f"audio_{message.message_id}"
    opts = BASE_YTDL_OPTS.copy()
    opts.update({
        'format': 'bestaudio/best',
        'outtmpl': f'downloads/{video_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    })
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
            
        final_mp3 = f"downloads/{video_id}.mp3"
        
        bot.edit_message_text("🚀 جاري رفع وإرسال ملف الـ MP3 إليك...", chat_id=message.chat.id, message_id=status_msg.message_id)
        
        with open(final_mp3, 'rb') as audio_file:
            bot.send_audio(message.chat.id, audio_file, caption="🎵 تم صيد وتحويل الصوت بنجاح باهر عبر السيرفر المطور!")
            
        os.remove(final_mp3)
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        
    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text("❌ فشل استخراج الـ MP3. يرجى التأكد من أن الحساب عام وإعادة المحاولة لاحقاً.", chat_id=message.chat.id, message_id=status_msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
