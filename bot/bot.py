import asyncio
import os
import requests
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from news import get_news
from trends import get_trends
from blog import save_draft

# Завантаження VADER для аналізу настрою
nltk.download('vader_lexicon', quiet=True)
sid = SentimentIntensityAnalyzer()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен із Render
HF_TOKEN = os.getenv("HF_TOKEN")  # Hugging Face токен
GOOGLE_TRANSLATE_KEY = os.getenv("GOOGLE_TRANSLATE_KEY")  # Google Translate ключ
CHANNEL_ID = "@HyperballoidAIArt"
X_TOKEN = os.getenv("X_TOKEN", "YOUR_X_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")
WP_URL = os.getenv("WP_URL", "YOUR_WORDPRESS_URL")
WP_AUTH = (os.getenv("WP_AUTH_USERNAME", "username"), os.getenv("WP_AUTH_PASSWORD", "password"))

# Статична база грантів
GRANTS_DB = [
    {"name": "NFT Art Grant", "url": "https://www.artstation.com", "deadline": "2025-06-01", "desc": "Грант для NFT-митців"},
    {"name": "AI Innovation Fund", "url": "https://www.grants.gov", "deadline": "2025-07-15", "desc": "Фонд для AI-проєктів"},
    {"name": "VR Creator Award", "url": "https://spatial.io", "deadline": "2025-05-30", "desc": "Нагорода для VR-арту"}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    if lang.startswith("uk"):
        await update.message.reply_text(
            "Привіт! Я бот @HyperballoidAIArt. Команди:\n"
            "/guide - Гайди (AI, NFT, VR)\n/nft - Мої NFT\n/news - Новини\n"
            "/trends - Тренди\n/poll - Опитування\n/giveaway - Розіграш\n"
            "/challenge - Челендж\n/prompt - Промпт для Leonardo.ai\n"
            "/draft - Чернетка статті\n/publish - Поширення\n/collab - Колаборації\n"
            "/contest - Конкурси\n/grants - Пошук грантів\n/chat - Поговори зі мною\n"
            "/analyze - Аналіз настрою тексту\n/postart - Поширення арту\n/invite - Запросити друзів"
        )
    else:
        await update.message.reply_text(
            "Hi! I'm @HyperballoidAIArt’s bot. Commands:\n"
            "/guide - Guides (AI, NFT, VR)\n/nft - My NFTs\n/news - News\n"
            "/trends - Trends\n/poll - Poll\n/giveaway - Raffle\n"
            "/challenge - Challenge\n/prompt - Leonardo.ai prompt\n"
            "/draft - Article draft\n/publish - Share\n/collab - Collabs\n"
            "/contest - Contests\n/grants - Search grants\n/chat - Talk to me\n"
            "/analyze - Analyze text sentiment\n/postart - Share art\n/invite - Invite friends"
        )

async def guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    topic = context.args[0] if context.args else "ai"
    guides_en = {
        "ai": "🎨 AI Art Guide:\n1. Go to leonardo.ai\n2. Use /prompt\n3. Mint on Binance (/buy)",
        "nft": "💸 NFT Guide:\n1. Join Binance NFT\n2. Mint with /nft\n3. Promote with /publish",
        "vr": "🕶️ VR Guide:\n1. Try Spatial.io\n2. Upload NFT\n3. Share with /vr"
    }
    guides_uk = {
        "ai": "🎨 Гайд з AI-арту:\n1. Зайди на leonardo.ai\n2. Спробуй /prompt\n3. Мінти на Binance (/buy)",
        "nft": "💸 Гайд з NFT:\n1. Приєднайся до Binance NFT\n2. Мінти з /nft\n3. Просувай з /publish",
        "vr": "🕶️ Гайд з VR:\n1. Спробуй Spatial.io\n2. Завантаж NFT\n3. Поділись з /vr"
    }
    guides = guides_uk if lang.startswith("uk") else guides_en
    await update.message.reply_text(guides.get(topic, "Використовуй /guide ai, /guide nft або /guide vr" if lang.startswith("uk") else "Use /guide ai, /guide nft, or /guide vr"))

async def nft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    caption = "Мій останній NFT! Мінти: https://www.binance.com/en/nft" if lang.startswith("uk") else "My latest NFT! Mint: https://www.binance.com/en/nft"
    try:
        await update.message.reply_photo(
            photo="https://hyperballoid.github.io/assets/nft/nft_1.png",
            caption=caption
        )
    except:
        await update.message.reply_text("NFT не знайдено. Додай зображення!" if lang.startswith("uk") else "NFT not found. Add an image!")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    try:
        articles = get_news(NEWSAPI_KEY)
        if not articles:
            raise Exception("No news")
        response = "\n".join(f"📰 {a['title']}: {a['url']}" for a in articles)
        if lang.startswith("uk"):
            await update.message.reply_text(f"Останні новини AI-арту:\n{response}")
        else:
            await update.message.reply_text(f"Latest AI art news:\n{response}")
    except:
        await update.message.reply_text("Помилка новин. Перевір NEWSAPI_KEY." if lang.startswith("uk") else "News error. Check NEWSAPI_KEY.")

async def trends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    try:
        trends = get_trends()
        response = ", ".join(trends)
        if lang.startswith("uk"):
            await update.message.reply_text(f"🔥 Тренди: {response}")
        else:
            await update.message.reply_text(f"🔥 Trends: {response}")
    except:
        await update.message.reply_text("Помилка трендів." if lang.startswith("uk") else "Trends error.")

async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    question = "Який стиль NFT наступний?" if lang.startswith("uk") else "Which NFT style next?"
    await update.message.reply_poll(
        question=question,
        options=["Cyberpunk", "Anime", "Abstract"],
        is_anonymous=False
    )

async def giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    text = "🎁 Виграй безкоштовний NFT! Підпишись на @HyperballoidAIArt і зроби репост у X!" if lang.startswith("uk") else "🎁 Win a free NFT! Follow @HyperballoidAIArt and retweet on X!"
    await update.message.reply_text(text)

async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    text = "🏆 Челендж: Створи AI-арт із /prompt і познач @HyperballoidAIArt!" if lang.startswith("uk") else "🏆 Challenge: Create AI art with /prompt and tag @HyperballoidAIArt!"
    await update.message.reply_text(text)

async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    topic = " ".join(context.args) or "cyberpunk Kyiv"
    prompt_text = f"{topic}, neon lights, 3000x3000px"
    if lang.startswith("uk"):
        await update.message.reply_text(f"Промпт для Leonardo.ai: '{prompt_text}'")
    else:
        await update.message.reply_text(f"Leonardo.ai prompt: '{prompt_text}'")

async def draft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    topic = " ".join(context.args) or "AI art trends"
    try:
        save_draft(topic)
        if lang.startswith("uk"):
            await update.message.reply_text(f"Чернетку збережено: {topic}. Перевір blog/{topic.replace(' ', '_')}.md")
        else:
            await update.message.reply_text(f"Draft saved: {topic}. Check blog/{topic.replace(' ', '_')}.md")
    except:
        await update.message.reply_text("Помилка чернетки. Спробуй ще." if lang.startswith("uk") else "Draft error. Try again.")

async def publish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    platform = context.args[0] if context.args else "all"
    topic = context.user_data.get("topic", "AI art update")
    message = f"Нове оновлення AI-арту! Приєднуйтесь: https://t.me/HyperballoidAIArt #NFTart" if lang.startswith("uk") else f"New AI art update! Join: https://t.me/HyperballoidAIArt #NFTart"
    
    try:
        if platform in ("tg", "all"):
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=message
            )
        if platform in ("x", "all") and X_TOKEN != "YOUR_X_TOKEN":
            requests.post(
                "https://api.twitter.com/2/tweets",
                headers={"Authorization": f"Bearer {X_TOKEN}"},
                json={"text": message}
            )
        if platform in ("wp", "all") and WP_URL != "YOUR_WORDPRESS_URL":
            requests.post(
                f"{WP_URL}/wp-json/wp/v2/posts",
                auth=WP_AUTH,
                json={"title": topic, "content": message, "status": "publish"}
            )
        await update.message.reply_text("Опубліковано!" if lang.startswith("uk") else "Published!")
    except:
        await update.message.reply_text("Помилка публікації." if lang.startswith("uk") else "Publish error.")

async def collab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    text = "🤝 Колаборації: Знайшов @AIArtistX на X для NFT-партнерства!" if lang.startswith("uk") else "🤝 Collabs: Found @AIArtistX on X for NFT partnership!"
    await update.message.reply_text(text)

async def contest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    text = "🏅 Конкурси: Спробуй гранти для митців! Використай /grants для деталей." if lang.startswith("uk") else "🏅 Contests: Try artist grants! Use /grants for details."
    await update.message.reply_text(text)

async def grants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    try:
        response = "\n".join(f"🏆 {g['name']} (до {g['deadline']}): {g['desc']} ({g['url']})" for g in GRANTS_DB)
        if lang.startswith("uk"):
            await update.message.reply_text(f"Доступні гранти:\n{response}\nДодай свої через GitHub!")
        else:
            await update.message.reply_text(f"Available grants:\n{response}\nAdd yours via GitHub!")
    except:
        await update.message.reply_text("Помилка пошуку грантів." if lang.startswith("uk") else "Grants search error.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Напиши щось для розмови, наприклад: /chat Що таке AI-арт?" if lang.startswith("uk") else "Write something to talk about, e.g., /chat What is AI art?")
        return
    
    try:
        # Переклад на англійську, якщо українська
        query_to_hf = query
        if lang.startswith("uk") and GOOGLE_TRANSLATE_KEY:
            response = requests.get(
                f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_TRANSLATE_KEY}",
                params={"q": query, "source": "uk", "target": "en"}
            )
            response.raise_for_status()
            query_to_hf = response.json()["data"]["translations"][0]["translatedText"]
        
        # Запит до Hugging Face
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": query_to_hf, "parameters": {"max_new_tokens": 100}}
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        answer = response.json()[0]["generated_text"]
        
        # Переклад відповіді на українську
        if lang.startswith("uk") and GOOGLE_TRANSLATE_KEY:
            response = requests.get(
                f"https://translation.googleapis.com/language/translate/v2?key={GOOGLE_TRANSLATE_KEY}",
                params={"q": answer, "source": "en", "target": "uk"}
            )
            response.raise_for_status()
            answer = response.json()["data"]["translations"][0]["translatedText"]
        
        await update.message.reply_text(answer)
    except:
        await update.message.reply_text("Помилка чату. Спробуй ще раз!" if lang.startswith("uk") else "Chat error. Try again!")

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Напиши текст для аналізу, наприклад: /analyze Я люблю AI-арт!" if lang.startswith("uk") else "Write text to analyze, e.g., /analyze I love AI art!")
        return
    
    try:
        scores = sid.polarity_scores(text)
        sentiment = "позитивний" if scores['compound'] > 0 else "негативний" if scores['compound'] < 0 else "нейтральний"
        if lang.startswith("uk"):
            await update.message.reply_text(f"Настрій тексту: {sentiment} (позитив: {scores['pos']}, негатив: {scores['neg']}, нейтральний: {scores['neu']})")
        else:
            await update.message.reply_text(f"Text sentiment: {sentiment} (positive: {scores['pos']}, negative: {scores['neg']}, neutral: {scores['neu']})")
    except:
        await update.message.reply_text("Помилка аналізу. Спробуй ще!" if lang.startswith("uk") else "Analysis error. Try again!")

async def postart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    if not update.message.photo:
        await update.message.reply_text(
            "Надішли зображення твоєї роботи!" if lang.startswith("uk") else "Send an image of your artwork!"
        )
        return
    
    # Зберігаємо фото
    photo = update.message.photo[-1]
    context.user_data["art_photo"] = photo.file_id
    
    # Генеруємо опис через Hugging Face
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": "Describe a digital artwork in a cyberpunk style", "parameters": {"max_new_tokens": 50}}
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        description = response.json()[0]["generated_text"]
    except:
        description = "A stunning digital artwork inspired by cyberpunk aesthetics."
    
    context.user_data["art_description"] = description
    
    # Запитуємо розмір
    await update.message.reply_text(
        f"Опис: {description}\nВкажи розмір (наприклад, 1080x1080):" if lang.startswith("uk")
        else f"Description: {description}\nSpecify size (e.g., 1080x1080):"
    )
    context.user_data["postart_step"] = "size"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    if context.user_data.get("postart_step") == "size":
        context.user_data["art_size"] = update.message.text
        context.user_data["postart_step"] = "confirm"
        
        # Показуємо чернетку
        photo = context.user_data["art_photo"]
        description = context.user_data["art_description"]
        size = context.user_data["art_size"]
        
        keyboard = [
            [InlineKeyboardButton("Підтвердити", callback_data="confirm_post"),
             InlineKeyboardButton("Скасувати", callback_data="cancel_post")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=f"Чернетка:\nОпис: {description}\nРозмір: {size}" if lang.startswith("uk")
            else f"Draft:\nDescription: {description}\nSize: {size}",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            "Надішли команду, наприклад, /postart!" if lang.startswith("uk")
            else "Send a command, e.g., /postart!"
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = update.effective_user.language_code
    
    if query.data == "confirm_post":
        photo = context.user_data["art_photo"]
        description = context.user_data["art_description"]
        size = context.user_data["art_size"]
        
        await query.message.reply_text(
            f"Опубліковано!\nОпис: {description}\nРозмір: {size}" if lang.startswith("uk")
            else f"Published!\nDescription: {description}\nSize: {size}"
        )
        context.user_data.clear()
    elif query.data == "cancel_post":
        await query.message.reply_text(
            "Скасовано." if lang.startswith("uk") else "Cancelled."
        )
        context.user_data.clear()

async def invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.effective_user.language_code
    text = "Запроси друзів до @HyperballoidAIArt для AI-арту та NFT! Лінк: https://t.me/HyperballoidAIArt" if lang.startswith("uk") else "Invite friends to @HyperballoidAIArt for AI art & NFTs! Link: https://t.me/HyperballoidAIArt"
    await update.message.reply_text(text)

async def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("guide", guide))
        application.add_handler(CommandHandler("nft", nft))
        application.add_handler(CommandHandler("news", news))
        application.add_handler(CommandHandler("trends", trends))
        application.add_handler(CommandHandler("poll", poll))
        application.add_handler(CommandHandler("giveaway", giveaway))
        application.add_handler(CommandHandler("challenge", challenge))
        application.add_handler(CommandHandler("prompt", prompt))
        application.add_handler(CommandHandler("draft", draft))
        application.add_handler(CommandHandler("publish", publish))
        application.add_handler(CommandHandler("collab", collab))
        application.add_handler(CommandHandler("contest", contest))
        application.add_handler(CommandHandler("grants", grants))
        application.add_handler(CommandHandler("chat", chat))
        application.add_handler(CommandHandler("analyze", analyze))
        application.add_handler(CommandHandler("postart", postart))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_handler(CommandHandler("invite", invite))

        await application.initialize()
        await application.start()
        await application.updater.start_polling(poll_interval=1.0, timeout=10, drop_pending_updates=True)
        print("Bot started")
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
