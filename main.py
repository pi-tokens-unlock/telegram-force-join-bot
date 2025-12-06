import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
import logging
import threading
from flask import Flask

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL = "@PInetAnnouncement"

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is Running 24/7 on Render!"


def run_flask():
    port = int(os.environ.get("PORT", 10000))  # ✅ Render PORT FIX
    app.run(host='0.0.0.0', port=port)

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

    except:
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
    except:
        query.edit_message_text("Join Channel First ✅", reply_markup=reply_markup)

def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(check_btn))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
