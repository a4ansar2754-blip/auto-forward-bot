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


# ---------------- CONFIG ----------------

def load_config():

    if not os.path.exists(CONFIG_FILE):

        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "sources": {},
                "targets": {},
                "settings": {
                    "forward": True,
                    "media": True,
                    "remove_links": False,
                    "remove_username": False,
                    "auto_delete": False,
                    "blacklist": []
                }
            }, f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- START PANEL ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [

        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],

        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],

        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]

    ]

    await update.message.reply_text(

        "🚀 AUTO FORWARD PANEL\n\nChoose option 👇",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )


# ---------------- PANEL ----------------

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    if query.data == "sources":

        mode = "source"

        keyboard = [[InlineKeyboardButton("📌 I have pinned the chats", callback_data="fetch_chats")]]

        await query.message.reply_text(

            "📥 Add SOURCE channel\n\nClick button below 👇",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )

    elif query.data == "targets":

        mode = "target"

        keyboard = [[InlineKeyboardButton("📌 I have pinned the chats", callback_data="fetch_chats")]]

        await query.message.reply_text(

            "🎯 Add TARGET channel\n\nClick button below 👇",

            reply_markup=InlineKeyboardMarkup(keyboard)

        )

    elif query.data == "dashboard":

        data = load_config()

        text = "📊 DASHBOARD\n\n"

        text += "📥 SOURCES\n"

        if data["sources"]:
            for s in data["sources"].values():
                text += f"• {s}\n"
        else:
            text += "None\n"

        text += "\n🎯 TARGETS\n"

        if data["targets"]:
            for t in data["targets"].values():
                text += f"• {t}\n"
        else:
            text += "None\n"

        await query.message.reply_text(text)


# ---------------- FETCH CHATS ----------------

async def fetch_chats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global chat_list

    query = update.callback_query
    await query.answer()

    dialogs = await client.get_dialogs()

    chat_list = dialogs[:15]

    text = "📋 SELECT CHAT NUMBER\n\n"

    for i, chat in enumerate(chat_list, start=1):
        text += f"{i}. {chat.name}\n"

    buttons = []
    row = []

    for i in range(1, len(chat_list) + 1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"addchat_{i}"))

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await query.message.reply_text(

        text,

        reply_markup=InlineKeyboardMarkup(buttons)

    )


# ---------------- ADD CHAT ----------------

async def add_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1]) - 1

    if index >= len(chat_list):
        await query.message.reply_text("❌ Invalid selection")
        return

    chat = chat_list[index]

    chat_id = str(chat.id)
    chat_name = chat.name

    data = load_config()

    if mode == "source":

        if chat_id in data["sources"]:
            await query.message.reply_text("❌ Already added in Sources")
            return

        data["sources"][chat_id] = chat_name

        await query.message.reply_text(f"✅ SOURCE ADDED\n📥 {chat_name}")

    elif mode == "target":

        if chat_id in data["targets"]:
            await query.message.reply_text("❌ Already added in Targets")
            return

        data["targets"][chat_id] = chat_name

        await query.message.reply_text(f"✅ TARGET ADDED\n🎯 {chat_name}")

    save_config(data)


# ---------------- SETTINGS COMMANDS ----------------

async def forward_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["forward"] = True
    save_config(data)
    await update.message.reply_text("✅ Forwarding ON")


async def forward_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["forward"] = False
    save_config(data)
    await update.message.reply_text("❌ Forwarding OFF")


async def media_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["media"] = True
    save_config(data)
    await update.message.reply_text("📸 Media Forwarding ON")


async def media_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["media"] = False
    save_config(data)
    await update.message.reply_text("📸 Media Forwarding OFF")


async def links_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["remove_links"] = True
    save_config(data)
    await update.message.reply_text("🔗 Links Removal ON")


async def links_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["remove_links"] = False
    save_config(data)
    await update.message.reply_text("🔗 Links Removal OFF")


async def username_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["remove_username"] = True
    save_config(data)
    await update.message.reply_text("👤 Username Removal ON")


async def username_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["remove_username"] = False
    save_config(data)
    await update.message.reply_text("👤 Username Removal OFF")


async def autodelete_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["auto_delete"] = True
    save_config(data)
    await update.message.reply_text("🗑 Auto Delete ON")


async def autodelete_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_config()
    data["settings"]["auto_delete"] = False
    save_config(data)
    await update.message.reply_text("🗑 Auto Delete OFF")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()
    s = data["settings"]

    text = f"""
⚙ CURRENT SETTINGS

Forward: {s["forward"]}
Media: {s["media"]}
Remove Links: {s["remove_links"]}
Remove Username: {s["remove_username"]}
Auto Delete: {s["auto_delete"]}
Blacklist: {s["blacklist"]}
"""

    await update.message.reply_text(text)


# ---------------- USERBOT START ----------------

async def on_startup(app):

    asyncio.create_task(start_userbot())


# ---------------- MAIN ----------------

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("forward_on", forward_on))
    app.add_handler(CommandHandler("forward_off", forward_off))

    app.add_handler(CommandHandler("media_on", media_on))
    app.add_handler(CommandHandler("media_off", media_off))

    app.add_handler(CommandHandler("links_on", links_on))
    app.add_handler(CommandHandler("links_off", links_off))

    app.add_handler(CommandHandler("username_on", username_on))
    app.add_handler(CommandHandler("username_off", username_off))

    app.add_handler(CommandHandler("autodelete_on", autodelete_on))
    app.add_handler(CommandHandler("autodelete_off", autodelete_off))

    app.add_handler(CommandHandler("settings", settings))

    app.add_handler(CallbackQueryHandler(panel, pattern="^(sources|targets|dashboard)$"))

    app.add_handler(CallbackQueryHandler(fetch_chats, pattern="^fetch_chats$"))

    app.add_handler(CallbackQueryHandler(add_chat, pattern=r"^addchat_\d+$"))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
