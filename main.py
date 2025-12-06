import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from flask import Flask, request # Flask এবং request ইমপোর্ট করা হয়েছে
import logging

# --- কনফিগারেশন ভেরিয়েবল (Render থেকে লোড হবে) ---
TOKEN = os.getenv("BOT_TOKEN")
# Render সার্ভারের জন্য পোর্ট
PORT = int(os.environ.get("PORT", 5000)) 
CHANNEL = "@PInetAnnouncement"
# Render-এর পাবলিক URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)
# Updater এবং Dispatcher গ্লোবাল হিসাবে সেট করা হলো
if TOKEN:
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
else:
    logging.error("BOT_TOKEN environment variable not found. Exiting.")
    exit() # টোকেন না পেলে বন্ধ করে দেওয়া হলো

# --- বটের মূল লজিক (অপরিবর্তিত) ---

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    download_message = "DOWNLOAD YOUR APK👇\n\n@JamesModz"

    try:
        member = context.bot.get_chat_member(CHANNEL, user_id) 

        if member.status in ['member', 'administrator', 'creator']:
            update.message.reply_text(download_message)
        else:
            keyboard = [
                [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL.lstrip('@')}")],
                [InlineKeyboardButton("✅ CHECK", callback_data="check")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text("Join Channel To Download ✅", reply_markup=reply_markup)

    except Exception as e:
        logging.error(f"Error in start: {e}")
        update.message.reply_text("First Join Our Channel ✅")


def check_btn(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()

    download_message = "DOWNLOAD YOUR APK👇\n\n@JamesModz"

    keyboard = [
        [InlineKeyboardButton("✅ Join Channel", url=f"https://t.me/{CHANNEL.lstrip('@')}")],
        [InlineKeyboardButton("✅ CHECK", callback_data="check")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        member = context.bot.get_chat_member(CHANNEL, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            query.edit_message_text(download_message)
        else:
            query.edit_message_text("Join Channel First ✅", reply_markup=reply_markup)
    except Exception as e:
        logging.error(f"Error in check_btn: {e}")
        query.edit_message_text("Join Channel First ✅", reply_markup=reply_markup)


# --- Webhook রুট ---

@app.route('/')
def home():
    return "Telegram Bot is Running via Webhook on Render!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.method == "POST":
        # JSON ডেটা থেকে টেলিগ্রাম আপডেট তৈরি করা 
        update = Update.de_json(request.get_json(force=True), dp.bot)
        # Dispatcher-কে আপডেট প্রক্রিয়া করতে বলা
        dp.process_update(update)
    return "ok"


# --- মূল ফাংশন যা বট চালু করবে ---

def main():
    # হ্যান্ডলার যোগ করা
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_btn))
    
    # Webhook সেট করা
    if WEBHOOK_URL and TOKEN:
        # set_webhook এ সম্পূর্ণ URL দিতে হবে
        webhook_url_full = WEBHOOK_URL.rstrip('/') + f'/{TOKEN}'
        updater.bot.set_webhook(url=webhook_url_full) 
        logging.info(f"Webhook set to: {webhook_url_full}")
    else:
        logging.error("WEBHOOK_URL not set in environment variables.")

    # Flask অ্যাপ চালানো
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)

if __name__ == "__main__":
    if TOKEN:
        main()
    else:
        logging.error("BOT_TOKEN environment variable not found. Check Render configuration.")
