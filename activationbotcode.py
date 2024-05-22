import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler, ContextTypes
import os
import requests

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states
SUBSCRIBE, CODE = range(2)

# Subscription keys for different durations
one_month_keys = ["sdfsdfs", "dvsasdgwr", "ddgsg"]
three_months_keys = ["3MKEY1", "3MKEY2", "3MKEY3"]
six_months_keys = ["6MKEY1", "6MKEY2", "hiu"]

REDIRECT_LINK = "https://google.com"
ADMIN_CHAT_ID = "1497001715"
USER_SECRET_FILE = 'user_secret.txt'
WEBHOOK_URL = 'https://hook.eu2.make.com/dfvhq6gyhlvqvtucyslb3p38qo6d31pq'
CHANNEL_URL = "https://t.me/dzrtalerts"  # Replace with your actual channel URL
ADMIN_URL = "https://t.me/rayyan43"  # Replace with your actual admin URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [InlineKeyboardButton("Buy Subscription", url=REDIRECT_LINK)],
        [InlineKeyboardButton("Activate Subscription", callback_data='subscribe')]
    ]
    message = '''🌟 مرحباً بك في بوت تتبع منتجات DZRT! 🌟

هذا البوت يساعدك على تتبع المنتجات المفضلة لديك والحصول على إشعارات عندما تكون متاحة. 🛍️

📌 قم بتحديد المنتجات التي تريد تلقي الإشعارات عنها، واستمتع بتجربة تسوق مميزة معنا!'''
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup)
    return SUBSCRIBE

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'subscribe':
        await query.edit_message_text(text="Enter the code to subscribe to the channel:")
        return CODE
    return ConversationHandler.END

def check_user_secret(username, code):
    if os.path.exists(USER_SECRET_FILE):
        with open(USER_SECRET_FILE, 'r') as file:
            lines = file.readlines()
            for line in lines:
                stored_username, stored_code = line.strip().split(': ')
                if stored_code == code:
                    if stored_username == username:
                        return 'same_user'
                    else:
                        return 'different_user'
    return 'not_found'

def add_user_secret(username, code):
    with open(USER_SECRET_FILE, 'a') as file:
        file.write(f'{username}: {code}\n')

async def code_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_code = update.message.text
    user = update.message.from_user
    username = user.username

    if user_code in one_month_keys:
        subscription_type = "1 month"
    elif user_code in three_months_keys:
        subscription_type = "3 months"
    elif user_code in six_months_keys:
        subscription_type = "6 months"
    else:
        await update.message.reply_text("Incorrect code. Please try again or type /cancel to stop.")
        return CODE

    check_result = check_user_secret(username, user_code)
    if check_result == 'different_user':
        await update.message.reply_text("This code is already in use by another user. Subscription failed.")
        return ConversationHandler.END
    elif check_result == 'not_found':
        add_user_secret(username, user_code)

    # Message to the user
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=CHANNEL_URL)],
        [InlineKeyboardButton("Contact Admin", url=ADMIN_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(f"Code correct for {subscription_type} subscription! Your request to join the private channel has been sent to the admin.", reply_markup=reply_markup)

    # Notify the admin
    admin_message = (
        f"🎉 New Subscription Request 🎉\n\n"
        f"👤 User: {user.full_name} (@{username})\n"
        f"📅 Subscription Type: {subscription_type}\n"
        f"🔑 Code: {user_code}\n\n"
        f"Please review and approve the request to add them to the channel."
    )
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_message)

    # Send details to webhook
    data = {
        'username': username,
        'subscription_type': subscription_type,
        'user_code': user_code
    }
    requests.post(WEBHOOK_URL, json=data)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Subscription process canceled.")
    return ConversationHandler.END

def main() -> None:
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token("6668479336:AAHeIAm_rYZ_fjraoaG0enSj2bwJb1mr29g").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SUBSCRIBE: [CallbackQueryHandler(button)],
            CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code_input)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()
