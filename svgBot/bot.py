import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправь мне картинку — я превращу её в SVG.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    temp_path = f"temp_{photo.file_id}.png"
    await file.download_to_drive(temp_path)

    with open(temp_path, "rb") as f:
        response = requests.post(API_URL, files={"file": f})

    os.remove(temp_path)

    data = response.json()
    print("API RESPONSE:", data)

    if data.get("status") != "success":
        await update.message.reply_text("❌ Ошибка обработки изображения.")
        return

    svg_file = data.get("svg_file")
    svg_url = data.get("svg_url")

    # 1. Отправляем SVG файл
    if svg_file and os.path.exists(svg_file):
        with open(svg_file, "rb") as f:
            await update.message.reply_document(f, caption="✅ SVG файл готов")

    # 2. Отправляем ссылку
    if svg_url:
        await update.message.reply_text(f"🔗 SVG ссылка:\n{svg_url}")

    # 3. Финальное сообщение
    await update.message.reply_text("🎉 Готово! Если хочешь — отправь ещё одно изображение.")

    photo = update.message.photo[-1]
    file = await photo.get_file()

    temp_path = f"temp_{photo.file_id}.png"
    await file.download_to_drive(temp_path)

    with open(temp_path, "rb") as f:
        response = requests.post(API_URL, files={"file": f})

    os.remove(temp_path)

    if response.status_code != 200:
        await update.message.reply_text("Ошибка сервера.")
        return

    data = response.json()
    print("API RESPONSE:", data)
    if "result_image" not in data:
        await update.message.reply_text("Ошибка обработки.")
        return

    svg_path = data["result_image"]

    with open(svg_path, "rb") as f:
        await update.message.reply_document(f)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

    print("Telegram bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
