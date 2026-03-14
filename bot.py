import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler,ContextTypes

from telethon import TelegramClient
from userbot_manager import start_userbot

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

login_state = {}
clients = {}

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Welcome\n\nUse /login to connect your telegram"
    )

async def login(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id

    login_state[user] = "phone"

    await update.message.reply_text(
        "Send phone number with country code\nExample:\n+919999999999"
    )

async def message_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    text = update.message.text

    if login_state.get(user) == "phone":

        client = TelegramClient(
            f"sessions/{user}",
            API_ID,
            API_HASH
        )

        await client.connect()

        await client.send_code_request(text)

        context.user_data["client"] = client

        login_state[user] = "otp"

        await update.message.reply_text("Send OTP code")

    elif login_state.get(user) == "otp":

        client = context.user_data["client"]

        await client.sign_in(code=text)

        await update.message.reply_text(
            "Login successful\nUserbot starting..."
        )

        login_state[user] = None

        asyncio.create_task(start_userbot(user))

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("login",login))

    from telegram.ext import MessageHandler,filters

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,message_handler))

    print("BOT RUNNING")

    app.run_polling()

if __name__ == "__main__":
    main()
