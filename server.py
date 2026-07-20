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
    await bot.send_message(chat_id=update.effective_chat.id, text="✅ البوت شغال!\n\nجرب /video أو /mp3")

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE, is_video: bool):
    if not context.args:
        await bot.send_message(chat_id=update.effective_chat.id, text="⚠️ أرسل الرابط بعد الأمر")
        return
    await bot.send_message(chat_id=update.effective_chat.id, text="⏳ جاري التحميل...")

# Setup
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("video", lambda u,c: download_media(u,c,True)))
application.add_handler(CommandHandler("mp3", lambda u,c: download_media(u,c,False)))

@app.route('/', methods=['GET'])
def home():
    return "Bot is running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = Update.de_json(request.get_json(), bot)
        asyncio.run(application.process_update(update))
    except:
        pass
    return 'ok', 200

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    print("Bot started successfully")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
