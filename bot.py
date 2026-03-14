import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from userbot_manager import login_user
from engine import start_engine, stop_engine

BOT_TOKEN = os.getenv("BOT_TOKEN")

login_state = {}
phone_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("Login", callback_data="login")],
        [InlineKeyboardButton("Start Forward", callback_data="start")],
        [InlineKeyboardButton("Stop Forward", callback_data="stop")]
    ]

    await update.message.reply_text(
        "AUTO FORWARD PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id

    login_state[user] = "PHONE"

    await update.message.reply_text(
        "Send phone number\nExample:\n+919876543210"
    )


async def login_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    text = update.message.text

    if user not in login_state:
        return

    state = login_state[user]

    if state == "PHONE":

        phone_data[user] = text

        r = await login_user(user, text)

        if r == "CODE":

            login_state[user] = "OTP"

            await update.message.reply_text("Send OTP")

    elif state == "OTP":

        r = await login_user(user, phone_data[user], code=text)

        if r == "SUCCESS":

            login_state.pop(user)

            await update.message.reply_text("Login Success")


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if q.data == "start":

        await start_engine(user)

        await q.message.reply_text("Forward Started")

    elif q.data == "stop":

        await stop_engine(user)

        await q.message.reply_text("Forward Stopped")


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))

    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, login_flow)
    )

    app.run_polling()


if __name__ == "__main__":
    main()
