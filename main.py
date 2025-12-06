import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler
from flask import Flask, request # Flask-এর setup সামান্য পরিবর্তন করা হয়েছে

# ----------------------------------------------------------------------
# ⭐ গ্লোবাল ভ্যারিয়েবল এবং লগিং সেটআপ ⭐
# Webhook-এর জন্য হোস্ট করার সময় Port, Token, এবং Webhook URL প্রয়োজন।
# এই মানগুলি পরিবেশ ভ্যারিয়েবল (Environment Variables) থেকে আসবে।

TOKEN = os.environ.get("BOT_TOKEN") # Render.com-এ সেট করবেন
CHANNEL = "@PInetAnnouncement"      # আপনার চ্যানেল

# Render-এ পোর্ট 10000-এ চলে (Render অটোমেটিক সেট করে)
PORT = int(os.environ.get('PORT', 8443))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL") # Render.com-এ সেট করবেন (আপনার রেন্ডার সাইটের URL)

# Setting up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# --- 1. /start command handler ---
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    download_message = "DOWNLOAD YOUR APK👇\n\n@JamesModz"

    try:
        # async-এ get_chat_member-এর জন্য await ব্যবহার করুন
        member = await context.bot.get_chat_member(CHANNEL, user_id)

        if member.status in ['member', 'administrator', 'creator']:
            await update.message.reply_text(download_message) 
        
        else:
            keyboard = [[
                InlineKeyboardButton("Click To Join Channel", url=f"https://t.me/{CHANNEL.lstrip('@')}"),
            ],
            [
                InlineKeyboardButton("CHECK", callback_data='check_subscription'),
            ]]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            message_text = "✅ Join Channel To Download Mod ✅" 

            await update.message.reply_text(
                message_text,
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text(
            f"✅ Frist Join Our Channel:\n\n{CHANNEL}\n\n(Error: {e})"
        )

# --- 2. Button click handler ---
async def check_subscription_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    
    await query.answer()

    join_keyboard = [[
        InlineKeyboardButton("❗️Click To Join Channel❗️", url=f"https://t.me/{CHANNEL.lstrip('@')}"),
    ],
    [
        InlineKeyboardButton("CHECK", callback_data='check_subscription'),
    ]]
    join_reply_markup = InlineKeyboardMarkup(join_keyboard)
    join_message_text = "✅ Join Channel To Download Mod ✅"
    download_message = "DOWNLOAD YOUR APK👇\n\n@JamesModz" 

    try:
        member = await context.bot.get_chat_member(CHANNEL, user_id)

        if member.status in ['member', 'administrator', 'creator']:
            await query.edit_message_text(
                download_message,
                reply_markup=None 
            )
        
        else:
            await query.edit_message_text(
                join_message_text,
                reply_markup=join_reply_markup
            )

    except Exception as e:
        logger.error(f"Error in callback query: {e}")
        
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as delete_e:
            logger.error(f"Error deleting message: {delete_e}")
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=join_message_text,
            reply_markup=join_reply_markup
        )

# ----------------------------------------------------------------------
# ⭐ Webhook Flask Setup (Render-এর জন্য) ⭐
# ----------------------------------------------------------------------

# 1. Application Builder
application = Application.builder().token(TOKEN).build()

# 2. Add Handlers to Application
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern='check_subscription'))


# 3. Flask Server Setup
app = Flask(__name__)

# '/' রুটটি Render-এর স্বাস্থ্য পরীক্ষার জন্য
@app.route('/')
def index():
    return "Telegram Bot Webhook is running!", 200

# এই রুটটি Telegram থেকে আসা প্রতিটি আপডেট গ্রহণ করবে
@app.route(f"/{TOKEN}", methods=["POST"])
async def telegram_webhook():
    # Telegram থেকে আসা JSON ডেটাটি গ্রহণ করা হচ্ছে
    update = Update.de_json(request.get_json(force=True), application.bot)
    
    # ডেটাটি Application-এর ডিসপ্যাচারে পাঠানো হচ্ছে
    await application.process_update(update)
    
    return "ok", 200 # Telegram-কে নিশ্চিত করা যে আপডেটটি সফলভাবে পাওয়া গেছে

# 4. Main execution block
if __name__ == '__main__':
    if not TOKEN or not WEBHOOK_URL:
        logger.error("BOT_TOKEN or WEBHOOK_URL environment variables not set!")
    else:
        # 5. Webhook সেটআপ: বট শুরু করার আগে Telegram-কে আপনার Webhook URL সেট করতে বলুন।
        # Render-এ এটি একবারই করতে হয়।
        application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
        logger.info(f"Webhook set to: {WEBHOOK_URL}/{TOKEN}")

        # 6. Flask অ্যাপ্লিকেশন শুরু করা
        # Render সার্ভার স্বয়ংক্রিয়ভাবে এটি run করবে
        # আমরা Gunicorn ব্যবহার করব, তাই এই লাইনটির প্রয়োজন নেই: app.run(host='0.0.0.0', port=PORT) 
        # কিন্তু লোকালি চালানোর জন্য এটি ব্যবহার করা যায়।
        pass # Render-এর জন্য gunicorn ব্যবহার করা হবে
