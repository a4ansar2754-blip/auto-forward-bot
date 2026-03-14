import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from userbot import client, start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")

CONFIG_FILE = "config.json"

pinned_chats = []
mode = None


# ================= CONFIG =================

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"sources": [], "targets": []}, f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
    ]

    await update.message.reply_text(
        "🚀 **Auto Forward Panel**\n\nSelect option below 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= PANEL =================

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    if query.data == "sources":

        mode = "source"

        keyboard = [
            [InlineKeyboardButton("📌 I have pinned the chats", callback_data="fetch_pins")]
        ]

        await query.message.reply_text(
            "📥 **Add Source Channels**\n\n"
            "1️⃣ Pin the channels\n"
            "2️⃣ Click button below 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "targets":

        mode = "target"

        keyboard = [
            [InlineKeyboardButton("📌 I have pinned the chats", callback_data="fetch_pins")]
        ]

        await query.message.reply_text(
            "🎯 **Add Target Channels**\n\n"
            "Pin target channels then press button 👇",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "dashboard":

        data = load_config()

        text = "📊 **Forwarding Dashboard**\n\n"

        text += "📥 **Sources**\n"

        if data["sources"]:
            for s in data["sources"]:
                try:
                    chat = await client.get_entity(int(s))
                    text += f"• {chat.title}\n"
                except:
                    text += "• Unknown channel\n"
        else:
            text += "None\n"

        text += "\n🎯 **Targets**\n"

        if data["targets"]:
            for t in data["targets"]:
                try:
                    chat = await client.get_entity(int(t))
                    text += f"• {chat.title}\n"
                except:
                    text += "• Unknown channel\n"
        else:
            text += "None\n"

        await query.message.reply_text(text)


# ================= FETCH PINNED =================

async def fetch_pinned(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global pinned_chats

    query = update.callback_query
    await query.answer()

    dialogs = await client.get_dialogs()

    pinned_chats = [d for d in dialogs if d.pinned]

    if not pinned_chats:
        await query.message.reply_text("❌ No pinned chats found")
        return

    text = "📋 **Select Chat Number**\n\n"

    for i, chat in enumerate(pinned_chats[:15], start=1):
        text += f"{i}. {chat.name}\n"

    buttons = []
    row = []

    for i in range(1, min(len(pinned_chats), 15) + 1):

        row.append(
            InlineKeyboardButton(f"{i}️⃣", callback_data=f"add_{i}")
        )

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ================= ADD CHAT =================

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1]) - 1

    chat = pinned_chats[index]

    chat_id = str(chat.id)

    data = load_config()

    if mode == "source":

        if chat_id not in data["sources"]:
            data["sources"].append(chat_id)
            save_config(data)

            await query.message.reply_text(f"✅ **Source Added**\n📥 {chat.name}")

        else:
            await query.message.reply_text("⚠️ Source already added")

    elif mode == "target":

        if chat_id not in data["targets"]:
            data["targets"].append(chat_id)
            save_config(data)

            await query.message.reply_text(f"✅ **Target Added**\n🎯 {chat.name}")

        else:
            await query.message.reply_text("⚠️ Target already added")


# ================= START USERBOT =================

async def on_startup(app):

    asyncio.create_task(start_userbot())


# ================= MAIN =================

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(panel, pattern="sources|targets|dashboard"))
    app.add_handler(CallbackQueryHandler(fetch_pinned, pattern="fetch_pins"))
    app.add_handler(CallbackQueryHandler(add_chat, pattern="add_"))

    print("🚀 BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
