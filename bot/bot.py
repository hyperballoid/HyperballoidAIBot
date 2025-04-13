from telegram.ext import Updater, CommandHandler, PollHandler
import requests
import json
import os
from news import get_news
from trends import get_trends
from blog import save_draft

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен із Render Environment
CHANNEL_ID = "@HyperballoidAIArt"
X_TOKEN = os.getenv("X_TOKEN", "YOUR_X_TOKEN")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "YOUR_NEWSAPI_KEY")
WP_URL = os.getenv("WP_URL", "YOUR_WORDPRESS_URL")
WP_AUTH = (os.getenv("WP_AUTH_USERNAME", "username"), os.getenv("WP_AUTH_PASSWORD", "password"))

def start(update, context):
    lang = update.message.from_user.language_code
    if lang.startswith("uk"):
        update.message.reply_text(
            "Привіт! Я бот @HyperballoidAIArt. Команди:\n"
            "/guide - Гайди (AI, NFT, VR)\n/nft - Мої NFT\n/news - Новини\n"
            "/trends - Тренди\n/poll - Опитування\n/giveaway - Розіграш\n"
            "/challenge - Челендж\n/prompt - Промпт для Leonardo.ai\n"
            "/draft - Чернетка статті\n/publish - Поширення\n/collab - Колаборації\n"
            "/contest - Конкурси\n/invite - Запросити друзів"
        )
    else:
        update.message.reply_text(
            "Hi! I'm @HyperballoidAIArt’s bot. Commands:\n"
            "/guide - Guides (AI, NFT, VR)\n/nft - My NFTs\n/news - News\n"
            "/trends - Trends\n/poll - Poll\n/giveaway - Raffle\n"
            "/challenge - Challenge\n/prompt - Leonardo.ai prompt\n"
            "/draft - Article draft\n/publish - Share\n/collab - Collabs\n"
            "/contest - Contests\n/invite - Invite friends"
        )

def guide(update, context):
    lang = update.message.from_user.language_code
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
    update.message.reply_text(guides.get(topic, "Використовуй /guide ai, /guide nft або /guide vr" if lang.startswith("uk") else "Use /guide ai, /guide nft, or /guide vr"))

def nft(update, context):
    lang = update.message.from_user.language_code
    caption = "Мій останній NFT! Мінти: https://www.binance.com/en/nft" if lang.startswith("uk") else "My latest NFT! Mint: https://www.binance.com/en/nft"
    update.message.reply_photo(
        "https://hyperballoid.github.io/assets/nft/nft_1.png",
        caption=caption
    )

def news(update, context):
    lang = update.message.from_user.language_code
    try:
        articles = get_news(NEWSAPI_KEY)
        if not articles:
            raise Exception("No news")
        response = "\n".join(f"📰 {a['title']}: {a['url']}" for a in articles)
        if lang.startswith("uk"):
            update.message.reply_text(f"Останні новини AI-арту:\n{response}")
        else:
            update.message.reply_text(f"Latest AI art news:\n{response}")
    except:
        update.message.reply_text("Помилка новин. Спробуй пізніше." if lang.startswith("uk") else "News error. Try later.")

def trends(update, context):
    lang = update.message.from_user.language_code
    try:
        trends = get_trends()
        response = ", ".join(trends)
        if lang.startswith("uk"):
            update.message.reply_text(f"🔥 Тренди: {response}")
        else:
            update.message.reply_text(f"🔥 Trends: {response}")
    except:
        update.message.reply_text("Помилка трендів." if lang.startswith("uk") else "Trends error.")

def poll(update, context):
    lang = update.message.from_user.language_code
    question = "Який стиль NFT наступний?" if lang.startswith("uk") else "Which NFT style next?"
    update.message.reply_poll(
        question=question,
        options=["Cyberpunk", "Anime", "Abstract"],
        is_anonymous=False
    )

def giveaway(update, context):
    lang = update.message.from_user.language_code
    text = "🎁 Виграй безкоштовний NFT! Підпишись на @HyperballoidAIArt і зроби репост у X!" if lang.startswith("uk") else "🎁 Win a free NFT! Follow @HyperballoidAIArt and retweet on X!"
    update.message.reply_text(text)

def challenge(update, context):
    lang = update.message.from_user.language_code
    text = "🏆 Челендж: Створи AI-арт із /prompt і познач @HyperballoidAIArt!" if lang.startswith("uk") else "🏆 Challenge: Create AI art with /prompt and tag @HyperballoidAIArt!"
    update.message.reply_text(text)

def prompt(update, context):
    lang = update.message.from_user.language_code
    topic = " ".join(context.args) or "cyberpunk Kyiv"
    prompt_text = f"{topic}, neon lights, 3000x3000px"
    if lang.startswith("uk"):
        update.message.reply_text(f"Промпт для Leonardo.ai: '{prompt_text}'")
    else:
        update.message.reply_text(f"Leonardo.ai prompt: '{prompt_text}'")

def draft(update, context):
    lang = update.message.from_user.language_code
    topic = " ".join(context.args) or "AI art trends"
    try:
        save_draft(topic)
        if lang.startswith("uk"):
            update.message.reply_text(f"Чернетку збережено: {topic}. Перевір blog/{topic.replace(' ', '_')}.md")
        else:
            update.message.reply_text(f"Draft saved: {topic}. Check blog/{topic.replace(' ', '_')}.md")
    except:
        update.message.reply_text("Помилка чернетки. Спробуй ще." if lang.startswith("uk") else "Draft error. Try again.")

def publish(update, context):
    lang = update.message.from_user.language_code
    platform = context.args[0] if context.args else "all"
    topic = context.user_data.get("topic", "AI art update")
    message = f"Нове оновлення AI-арту! Приєднуйтесь: https://t.me/HyperballoidAIArt #NFTart" if lang.startswith("uk") else f"New AI art update! Join: https://t.me/HyperballoidAIArt #NFTart"
    
    try:
        if platform in ("tg", "all"):
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHANNEL_ID, "text": message}
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
        update.message.reply_text("Опубліковано!" if lang.startswith("uk") else "Published!")
    except:
        update.message.reply_text("Помилка публікації." if lang.startswith("uk") else "Publish error.")

def collab(update, context):
    lang = update.message.from_user.language_code
    text = "🤝 Колаборації: Знайшов @AIArtistX на X для NFT-партнерства!" if lang.startswith("uk") else "🤝 Collabs: Found @AIArtistX on X for NFT partnership!"
    update.message.reply_text(text)

def contest(update, context):
    lang = update.message.from_user.language_code
    text = "🏅 Конкурс: NFT-челендж на ArtStation, дедлайн 1 травня. Подай через /nft!" if lang.startswith("uk") else "🏅 Contest: NFT challenge on ArtStation, deadline May 1. Submit via /nft!"
    update.message.reply_text(text)

def invite(update, context):
    lang = update.message.from_user.language_code
    text = "Запроси друзів до @HyperballoidAIArt для AI-арту та NFT! Лінк: https://t.me/HyperballoidAIArt" if lang.startswith("uk") else "Invite friends to @HyperballoidAIArt for AI art & NFTs! Link: https://t.me/HyperballoidAIArt"
    update.message.reply_text(text)

def main():
    updater = Updater(BOT_TOKEN, use_context=True, request_kwargs={'read_timeout': 10, 'connect_timeout': 10})
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("guide", guide))
    dp.add_handler(CommandHandler("nft", nft))
    dp.add_handler(CommandHandler("news", news))
    dp.add_handler(CommandHandler("trends", trends))
    dp.add_handler(CommandHandler("poll", poll))
    dp.add_handler(CommandHandler("giveaway", giveaway))
    dp.add_handler(CommandHandler("challenge", challenge))
    dp.add_handler(CommandHandler("prompt", prompt))
    dp.add_handler(CommandHandler("draft", draft))
    dp.add_handler(CommandHandler("publish", publish))
    dp.add_handler(CommandHandler("collab", collab))
    dp.add_handler(CommandHandler("contest", contest))
    dp.add_handler(CommandHandler("invite", invite))
    updater.start_polling(poll_interval=1.0, timeout=10, clean=True)
    updater.idle()

if __name__ == "__main__":
    main()
