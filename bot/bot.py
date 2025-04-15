import os
import asyncio
import logging
import io
import nltk
import pytumblr
import requests
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Завантаження токенів із .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
GOOGLE_TRANSLATE_KEY = os.getenv("GOOGLE_TRANSLATE_KEY")
TUMBLR_CLIENT = pytumblr.TumblrRestClient(
    os.getenv("TUMBLR_KEY"),
    os.getenv("TUMBLR_SECRET"),
    os.getenv("TUMBLR_TOKEN"),
    os.getenv("TUMBLR_TOKEN_SECRET")
)
PINTEREST_TOKEN = os.getenv("PINTEREST_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Ініціалізація NLTK для аналізу
try:
    nltk.data.find("vader_lexicon")
except LookupError:
    nltk.download("vader_lexicon")
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start: Вітання та список команд"""
    await update.message.reply_text(
        "Привіт! Я @HyperballoidArtBot. Команди:\n"
        "/chat <запит> — спілкуйся українською\n"
        "/postart — опублікуй AI-арт у Tumblr\n"
        "/analyze <текст> — аналіз настрою\n"
        "/grants — актуальні гранти\n"
        "/publish tg — пост у @HyperballoidAIArt"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /chat: Переклад і відповідь"""
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Напиши запит, наприклад: /chat Що таке AI?")
        return

    lang = update.message.from_user.language_code or "uk"
    logger.info(f"Chat query: {query}, language: {lang}")

    if lang.startswith("uk") and GOOGLE_TRANSLATE_KEY:
        try:
            # Переклад українською → англійською
            response = requests.get(
                f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_TRANSLATE_KEY}",
                params={"q": query, "source": "uk", "target": "en"}
            )
            response.raise_for_status()
            translated = response.json()["data"]["translations"][0]["translatedText"]

            # Заглушка для AI-відповіді (можна додати Hugging Face)
            answer = f"Відповідь на '{translated}': Це цікаве питання!"

            # Переклад назад на українську
            response = requests.get(
                f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_TRANSLATE_KEY}",
                params={"q": answer, "source": "en", "target": "uk"}
            )
            response.raise_for_status()
            final_answer = response.json()["data"]["translations"][0]["translatedText"]
            await update.message.reply_text(final_answer)
        except requests.RequestException as e:
            logger.error(f"Translation error: {e}")
            await update.message.reply_text("Помилка перекладу. Спробуй ще!")
    else:
        await update.message.reply_text("Підтримується лише українська (/chat <запит>).")

async def postart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /postart: Публікація фото в Tumblr"""
    if update.message.photo:
        try:
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            photo_bytes = await file.download_as_bytearray()
            TUMBLR_CLIENT.create_photo(
                "hyperballoid-art",  # Заміни на свій Tumblr-блог
                state="published",
                tags=["AI art", "Hyperballoid"],
                data=io.BytesIO(photo_bytes)
            )
            await update.message.reply_text("Опубліковано в Tumblr!")
        except Exception as e:
            logger.error(f"Tumblr post error: {e}")
            await update.message.reply_text("Помилка публікації. Перевір токени!")
    else:
        await update.message.reply_text("Надішли фото для публікації!")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /analyze: Аналіз настрою тексту"""
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Напиши текст, наприклад: /analyze Я щасливий!")
        return

    scores = sia.polarity_scores(text)
    sentiment = "позитивний" if scores["compound"] > 0 else "негативний" if scores["compound"] < 0 else "нейтральний"
    await update.message.reply_text(f"Настрій тексту: {sentiment} (індекс: {scores['compound']:.2f})")

async def grants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /grants: Список грантів"""
    # Заглушка: можна додати API (наприклад, fundsforNGOs)
    grants_list = (
        "1. Грант на AI-мистецтво від Creative Europe\n"
        "2. Програма Horizon Europe для інновацій\n"
        "3. Локальні гранти від Мінкультури України"
    )
    await update.message.reply_text(f"Актуальні гранти:\n{grants_list}")

async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /publish: Публікація в канал"""
    platform = " ".join(context.args).lower()
    if platform == "tg":
        # Заглушка: можна додати Telegram API для @HyperballoidAIArt
        await update.message.reply_text("Пост опубліковано в @HyperballoidAIArt!")
    else:
        await update.message.reply_text("Вкажи платформу: /publish tg")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обробка помилок"""
    logger.error(f"Update {update} caused error: {context.error}")
    if update and update.message:
        await update.message.reply_text("Виникла помилка. Спробуй ще раз!")

async def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in .env")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # Реєстрація команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat", chat))
    application.add_handler(CommandHandler("postart", postart))
    application.add_handler(CommandHandler("analyze", analyze))
    application.add_handler(CommandHandler("grants", grants))
    application.add_handler(CommandHandler("publish", publish))

    # Обробка помилок
    application.add_error_handler(error_handler)

    logger.info("Starting bot...")
    await application.initialize()
    await application.updater.start_polling(poll_interval=1.0, timeout=10, drop_pending_updates=True)
    logger.info("Bot started")
    await application.start()

if __name__ == "__main__":
    asyncio.run(main())
