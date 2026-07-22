import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8836632507:AAGe1mHJMBlRaLCUoveAJA_j700xUvxNWEQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🎬 مرحباً {update.effective_user.first_name} في **بوت صيد الميديا الأقوى** ⚡\n\n"
        "🔹 `/video رابط` → تحميل فيديو (مع ضغط تلقائي إذا كان كبير)\n"
        "🔹 `/mp3 رابط` → تحميل صوت MP3 عالي الجودة\n\n"
        "🌐 يدعم: يوتيوب، إنستغرام، تيك توك، فيسبوك وأكثر!"
    )

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE, media_type: str):
    if not context.args:
        await update.message.reply_text("⚠️ يرجى إرسال الرابط بعد الأمر")
        return
    
    url = context.args[0].strip()
    status_msg = await update.message.reply_text("⏳ جاري التحميل من السيرفر السحابي...")

    # 🔥 تحديث الإعدادات هنا لدمج عملاء الهواتف الرسمية لتخطي حظر يوتيوب وتيك توك تلقائياً
    base_opts = {
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'restrictfilenames': True,
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'socket_timeout': 35,
        'extractor_retries': 3,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android'], # محاكاة هواتف لتجاوز حظر السيرفرات السحابية
                'skip': ['dash', 'hls']
            },
            'tiktok': {
                'app_version': ['20.2.1']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        },
    }

    try:
        if media_type == "video":
            ydl_opts = {**base_opts, 'format': 'bestvideo+bestaudio/best'}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            
            file_size_mb = os.path.getsize(filename) / (1024 * 1024)
            await status_msg.edit_text(f"✅ تم التحميل ({file_size_mb:.1f} MB). جاري التجهيز...")

            final_filename = filename

            # ضغط تلقائي إذا تجاوز 48 ميجا
            if file_size_mb > 48:
                await status_msg.edit_text(f"📦 الفيديو كبير ({file_size_mb:.1f} MB).\nجاري الضغط بذكاء لتليجرام...")
                
                compressed = f"downloads/compressed_{os.path.basename(filename)}"
                
                # ضغط احترافي
                os.system(
                    f'ffmpeg -i "{filename}" '
                    f'-vf "scale=1280:-2" '
                    f'-c:v libx264 -crf 27 -preset medium '
                    f'-c:a aac -b:a 128k '
                    f'-movflags +faststart '
                    f'"{compressed}" -y'
                )
                
                if os.path.exists(compressed) and os.path.getsize(compressed) > 10000:
                    if os.path.exists(filename):
                        os.remove(filename)
                    final_filename = compressed
                    new_size = os.path.getsize(final_filename) / (1024 * 1024)
                    await status_msg.edit_text(f"✅ تم الضغط بنجاح! ({new_size:.1f} MB)")
                else:
                    await status_msg.edit_text("⚠️ الضغط لم ينجح، سيتم إرسال الملف الأصلي.")

            # إرسال الفيديو
            await status_msg.edit_text("📤 جاري الإرسال إليك...")
            with open(final_filename, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    caption=f"✅ تم التحميل بنجاح بواسطة بوت عُمر السحابي!\n"
                            f"📏 الحجم: {os.path.getsize(final_filename)/(1024*1024):.1f} MB\n"
                            f"🌐 المصدر: {url[:50]}..."
                )
            
            # تنظيف
            for f_path in [filename, final_filename]:
                if os.path.exists(f_path):
                    os.remove(f_path)

        else:  # MP3
            ydl_opts = {
                **base_opts,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'keepvideo': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                base = ydl.prepare_filename(info)
                filename = os.path.splitext(base)[0] + '.mp3'
            
            await status_msg.edit_text("📤 جاري إرسال الملف الصوتي...")
            with open(filename, 'rb') as f:
                await update.message.reply_audio(
                    audio=f,
                    caption="✅ تم تحويل المقطع إلى MP3 بجودة 192kbps!\n🎵 بوت صيد الميديا"
                )
            if os.path.exists(filename):
                os.remove(filename)

    except Exception as e:
        error = str(e).lower()
        if "403" in error or "forbidden" in error or "sign in" in error:
            await status_msg.edit_text("❌ يوتيوب يفرض حظر حماية على هذا الرابط حالياً.")
        elif "unavailable" in error or "private" in error:
            await status_msg.edit_text("❌ الفيديو غير متاح أو خاص.")
        else:
            await status_msg.edit_text(f"❌ خطأ: {str(e)[:180]}")

def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("video", lambda u, c: download_media(u, c, "video")))
    app.add_handler(CommandHandler("mp3", lambda u, c: download_media(u, c, "mp3")))
    
    print("[+] 🚀 بوت صيد الميديا الأقوى شغال الآن بالتحصين البرمجي...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
