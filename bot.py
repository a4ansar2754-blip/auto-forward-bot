import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from userbot import start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")

CONFIG_FILE = "config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump({"sources": [], "targets": []}, f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


# START PANEL
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


# BUTTON PANEL
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "sources":

        data = load_config()
        sources = "\n".join(data["sources"]) if data["sources"] else "No sources added"

        await query.message.reply_text(
            f"📥 SOURCES\n\n{sources}\n\nAdd with:\n/addsource -100xxxx"
        )

    elif query.data == "targets":

        data = load_config()
        targets = "\n".join(data["targets"]) if data["targets"] else "No targets added"

        await query.message.reply_text(
            f"🎯 TARGETS\n\n{targets}\n\nAdd with:\n/addtarget -100xxxx"
        )

    elif query.data == "settings":

        await query.message.reply_text(
            "⚙ Settings panel coming soon"
        )

    elif query.data == "dashboard":

        data = load_config()

        await query.message.reply_text(
            f"📊 DASHBOARD\n\n"
            f"Sources: {len(data['sources'])}\n"
            f"Targets: {len(data['targets'])}"
        )


# ADD SOURCE
async def add_source(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/addsource -100123456789"
        )
        return

    source = context.args[0]

    data = load_config()

    if source not in data["sources"]:
        data["sources"].append(source)
        save_config(data)

    await update.message.reply_text(
        f"✅ Source Added\n{source}"
    )


# ADD TARGET
async def add_target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "Usage:\n/addtarget -100123456789"
        )
        return

    target = context.args[0]

    data = load_config()

    if target not in data["targets"]:
        data["targets"].append(target)
        save_config(data)

    await update.message.reply_text(
        f"✅ Target Added\n{target}"
    )


# USERBOT START
async def on_startup(app):

    print("USERBOT STARTING...")
    asyncio.create_task(start_userbot())


# MAIN
def main():

    print("BOT RUNNING")

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addsource", add_source))
    app.add_handler(CommandHandler("addtarget", add_target))

    app.add_handler(CallbackQueryHandler(panel))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
