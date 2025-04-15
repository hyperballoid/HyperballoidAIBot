import os
import asyncio
import logging
import nltk
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
        "/chat <запит> — спілкуйся\n"
        "/analyze <текст> — аналіз настрою\n"
        "/grants — актуальні гранти\n"
        "/publish tg — пост у @HyperballoidAIArt"
    )

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /chat: Базова відповідь (заглушка для AI)"""
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Напиши запит, наприклад: /chat Що таке AI?")
        return

    logger.info(f"Chat query: {query}")
    # Заглушка для AI (можна додати Hugging Face із HF_TOKEN)
    answer = f"Відповідь на '{query}': Це цікаве питання!"
    await update.message.reply_text(answer)

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
    # Заглушка: можна додати NewsAPI
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
        # Заглушка для @HyperballoidAIArt
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
