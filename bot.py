import asyncio
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from userbot import start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Targets", callback_data="targets")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
    ]

    await update.message.reply_text(
        "🚀 Welcome to Auto Forward Panel",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "sources":
        await query.message.reply_text("📥 Source panel coming soon")

    elif query.data == "targets":
        await query.message.reply_text("🎯 Target panel coming soon")

    elif query.data == "settings":
        await query.message.reply_text("⚙ Settings panel coming soon")

    elif query.data == "dashboard":
        await query.message.reply_text("📊 Dashboard coming soon")


app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(panel))


async def main():

    print("BOT RUNNING")

    # start telegram account
    asyncio.create_task(start_userbot())

    # start bot
    await app.run_polling()


asyncio.run(main())
