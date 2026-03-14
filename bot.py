import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from userbot import client, start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")

CONFIG_FILE = "config.json"

chat_list = []
mode = None


def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"sources": {}, "targets": {}}, f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
    ]

    await update.message.reply_text(
        "🚀 **Auto Forward Panel**\n\nSelect option below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    if query.data == "sources":

        mode = "source"

        keyboard = [
            [InlineKeyboardButton("📂 Show Chats", callback_data="fetch_chats")]
        ]

        await query.message.reply_text(
            "📥 **Add Source Channels**\n\nClick button to load chats 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "targets":

        mode = "target"

        keyboard = [
            [InlineKeyboardButton("📂 Show Chats", callback_data="fetch_chats")]
        ]

        await query.message.reply_text(
            "🎯 **Add Target Channels**\n\nClick button to load chats 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "dashboard":

        data = load_config()

        text = "📊 **Forwarding Dashboard**\n\n"

        text += "📥 **Sources**\n"

        if data["sources"]:
            for name in data["sources"].values():
                text += f"• {name}\n"
        else:
            text += "None\n"

        text += "\n🎯 **Targets**\n"

        if data["targets"]:
            for name in data["targets"].values():
                text += f"• {name}\n"
        else:
            text += "None\n"

        await query.message.reply_text(text, parse_mode="Markdown")


async def fetch_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global chat_list

    query = update.callback_query
    await query.answer()

    dialogs = await client.get_dialogs()

    chat_list = dialogs[:15]

    text = "📋 **Select Chat Number**\n\n"

    for i, chat in enumerate(chat_list, start=1):
        text += f"{i}. {chat.name}\n"

    buttons = []
    row = []

    for i in range(1, len(chat_list) + 1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"add_{i}"))

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="Markdown"
    )


async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1]) - 1

    chat = chat_list[index]

    chat_id = str(chat.id)
    chat_name = chat.name

    data = load_config()

    if mode == "source":

        data["sources"][chat_id] = chat_name

        await query.message.reply_text(
            f"✅ **Source Added**\n📥 {chat_name}",
            parse_mode="Markdown"
        )

    elif mode == "target":

        data["targets"][chat_id] = chat_name

        await query.message.reply_text(
            f"✅ **Target Added**\n🎯 {chat_name}",
            parse_mode="Markdown"
        )

    save_config(data)


async def on_startup(app):
    asyncio.create_task(start_userbot())


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(panel, pattern="sources|targets|dashboard"))
    app.add_handler(CallbackQueryHandler(fetch_chats, pattern="fetch_chats"))
    app.add_handler(CallbackQueryHandler(add_chat, pattern="add_"))

    print("🚀 BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
