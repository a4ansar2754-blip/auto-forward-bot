import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from userbot import client, start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")

CONFIG_FILE = "config.json"

pinned_cache = []


def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"sources": [], "targets": []}, f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


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

        keyboard = [
            [InlineKeyboardButton("✅ I have pinned the chats", callback_data="fetch_sources")]
        ]

        await query.message.reply_text(
            "📌 Pin the chats you want as SOURCE\n\n"
            "1. Go to chats\n"
            "2. Pin them\n"
            "3. Click button below",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "targets":

        keyboard = [
            [InlineKeyboardButton("✅ I have pinned the chats", callback_data="fetch_targets")]
        ]

        await query.message.reply_text(
            "📌 Pin the chats you want as TARGET",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "dashboard":

        data = load_config()

        await query.message.reply_text(
            f"📊 DASHBOARD\n\n"
            f"Sources: {len(data['sources'])}\n"
            f"Targets: {len(data['targets'])}"
        )


async def fetch_pinned(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global pinned_cache

    query = update.callback_query
    await query.answer()

    dialogs = await client.get_dialogs()

    pinned_cache = []

    for d in dialogs:
        if d.pinned:
            pinned_cache.append(d)

    if not pinned_cache:
        await query.message.reply_text("❌ No pinned chats found")
        return

    text = "🎯 Select Chat Number\n\n"

    for i, chat in enumerate(pinned_cache[:15], start=1):
        text += f"{i}. {chat.name}\n"

    buttons = []
    row = []

    for i in range(1, min(len(pinned_cache), 15) + 1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"select_{i}"))

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def select_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    num = int(query.data.split("_")[1]) - 1

    chat = pinned_cache[num]

    chat_id = str(chat.id)

    data = load_config()

    if "source_mode" in context.user_data:

        if chat_id not in data["sources"]:
            data["sources"].append(chat_id)

        await query.message.reply_text(f"✅ Source Added\n{chat.name}")

    else:

        if chat_id not in data["targets"]:
            data["targets"].append(chat_id)

        await query.message.reply_text(f"✅ Target Added\n{chat.name}")

    save_config(data)


async def on_startup(app):
    asyncio.create_task(start_userbot())


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(fetch_pinned, pattern="fetch_"))
    app.add_handler(CallbackQueryHandler(select_chat, pattern="select_"))
    app.add_handler(CallbackQueryHandler(panel))

    app.run_polling()


if __name__ == "__main__":
    main()
