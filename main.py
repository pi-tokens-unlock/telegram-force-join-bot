import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from flask import Flask, request # 'request' ইমপোর্ট করা হয়েছে
import logging
# threading এর আর দরকার নেই, তাই এটি বাদ দেওয়া হয়েছে

# --- কনফিগারেশন ভেরিয়েবল ---
TOKEN = os.getenv("BOT_TOKEN")
# Render স্বয়ংক্রিয়ভাবে একটি PORT বরাদ্দ করে, যা os.environ.get("PORT") থেকে নেওয়া হয়
PORT = int(os.environ.get("PORT", 5000)) # Render-এ 10000 এর পরিবর্তে 5000 বা 8080 ব্যবহার করা সাধারণ
CHANNEL = "@PInetAnnouncement"

# আপনার Render ওয়েব সার্ভিসের পাবলিক URL এখানে দিন
# এটি অবশ্যই Render এনভায়রনমেন্ট ভেরিয়েবল (WEBHOOK_URL) হিসেবে সেট করতে হবে
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- বটের মূল লজিক (অপরিবর্তিত) ---

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    download_message = "DOWNLOAD YOUR APK👇\n\n@JamesModz"

    try:
        # get_chat_member ফাংশনটি সফলভাবে চালাতে try-except ব্লক অপরিহার্য
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
        # logging.error(f"Error in start function: {e}") # ডিবাগিং এর জন্য
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
        # logging.error(f"Error in check_btn function: {e}") # ডিবাগিং এর জন্য
        query.edit_message_text("Join Channel First ✅", reply_markup=reply_markup)


# --- ওয়েবহুক সেটআপ ---

# 1. রুট পেজ, Render এর স্বাস্থ্য পরীক্ষা (Health Check) এর জন্য
@app.route('/')
def home():
    return f"Telegram Bot is Running via Webhook on Render! Listening on port {PORT}"

# 2. Telegram থেকে আপডেট গ্রহণের জন্য মূল ওয়েবহুক রুট
# আমরা URL এ BOT_TOKEN ব্যবহার করি সুরক্ষার জন্য
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.method == "POST":
        # JSON ডেটা থেকে টেলিগ্রাম আপডেট তৈরি করা 
        update = Update.de_json(request.get_json(force=True), updater.bot)
        # Dispatcher-কে আপডেট প্রক্রিয়া করতে বলা
        dp.process_update(update)
    return "ok"


# --- বটের শুরু এবং Webhook সেট করা ---

def main():
    # Updater এবং Dispatcher গ্লোবাল হিসাবে সেট করা হলো যাতে ওয়েবহুক ফাংশন এটি অ্যাক্সেস করতে পারে
    global updater, dp
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # হ্যান্ডলার যোগ করা
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_btn))
    
    # Telegram সার্ভারে Webhook সেট করা হচ্ছে
    if WEBHOOK_URL and TOKEN:
        # set_webhook এ সম্পূর্ণ URL দিতে হবে
        webhook_url_full = WEBHOOK_URL + TOKEN
        
        # PING করার জন্য URL এ /TOKEN যোগ করা হলো
        updater.bot.set_webhook(url=webhook_url_full) 
        logging.info(f"Webhook set to: {webhook_url_full}")
    else:
        logging.error("WEBHOOK_URL or BOT_TOKEN not set in environment variables.")

    # Flask অ্যাপ চালানো (এটি পোলিং এর পরিবর্তে সার্ভারকে সচল রাখবে)
    # use_reloader=False ব্যবহার করুন
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)

if __name__ == "__main__":
    if TOKEN:
        main()
    else:
        logging.error("BOT_TOKEN environment variable not found. Exiting.")
