from telegram.ext import Updater, CommandHandler, PollHandler
import requests
import json
from datetime import datetime

BOT_TOKEN = "7884645795:AAHSdUVQXkaX3iuCb3sTMl2iNGnQtLTWYwI"  # Вставиш на кроці 5
CHANNEL_ID = "@HyperballoidAIArt"

def start(update, context):
    lang = update.message.from_user.language_code
    if lang.startswith("uk"):
        update.message.reply_text(
            "Привіт! Я бот @HyperballoidAIArt. Команди:\n"
            "/guide - Гайди\n/nft - NFT\n/trends - Тренди\n/giveaway - Розіграш"
        )
    else:
        update.message.reply_text(
            "Hi! I'm @HyperballoidAIArt’s bot. Commands:\n"
            "/guide - Guides\n/nft - NFTs\n/trends - Trends\n/giveaway - Raffle"
        )

def guide(update, context):
    topic = context.args[0] if context.args else "ai"
    guides = {
        "ai": "🎨 AI Art Guide:\n1. Go to leonardo.ai\n2. Try /prompt\n3. Mint (/buy)",
        "nft": "💸 NFT Guide:\n1. Join Binance NFT\n2. Mint with /nft\n3. Share",
        "vr": "🕶️ VR Guide:\n1. Try Spatial.io\n2. Upload NFT\n3. Share with /vr"
    }
    update.message.reply_text(guides.get(topic, "Use /guide ai, /guide nft, or /guide vr"))

def nft(update, context):
    update.message.reply_photo(
        "https://hyperballoid.github.io/assets/nft/nft_1.png",
        caption="My latest NFT! Mint: https://www.binance.com/en/nft"
    )

def trends(update, context):
    update.message.reply_text("🔥 Trends: Cyberpunk and anime NFTs are hot! #Web3")

def giveaway(update, context):
    update.message.reply_text(
        "🎁 Win a free NFT! Follow @HyperballoidAIArt and retweet my X post!"
    )

def prompt(update, context):
    topic = " ".join(context.args) or "cyberpunk Kyiv"
    prompt_text = f"{topic}, neon lights, 3000x3000px"
    update.message.reply_text(f"Leonardo.ai prompt: '{prompt_text}'")

def publish(update, context):
    message = "New AI art update! Join @HyperballoidAIArt: https://t.me/HyperballoidAIArt #NFTart"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={"chat_id": CHANNEL_ID, "text": message}
    )
    update.message.reply_text("Posted to @HyperballoidAIArt!")

def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("guide", guide))
    dp.add_handler(CommandHandler("nft", nft))
    dp.add_handler(CommandHandler("trends", trends))
    dp.add_handler(CommandHandler("giveaway", giveaway))
    dp.add_handler(CommandHandler("prompt", prompt))
    dp.add_handler(CommandHandler("publish", publish))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
