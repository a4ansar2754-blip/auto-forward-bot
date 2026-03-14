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


# PANEL BUTTONS
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
        await update.message.reply_text("Usage:\n/addsource -100123456789")
        return

    source = context.args[0]

    data = load_config()

    if source not in data["sources"]:
        data["sources"].append(source)
        save_config(data)

    await update.message.reply_text(f"✅ Source Added\n{source}")


# ADD TARGET
async def add_target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text("Usage:\n/addtarget -100123456789")
        return

    target = context.args[0]

    data = load_config()

    if target not in data["targets"]:
        data["targets"].append(target)
        save_config(data)

    await update.message.reply_text(f"✅ Target Added\n{target}")


# TARGET UI (Best Auto Forward Style)
async def target_ui(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("✅ I have pinned the chats", callback_data="pinned")]
    ]

    text = (
        "Follow These Steps to Set Target Channels\n\n"
        "1. Go to the Chats From Which You Want to Copy Messages.\n"
        "2. Press and Hold the Source Channel.\n"
        "3. Tap on the Pin Icon to Pin it At the Top.\n\n"
        "⚠ Note: Make Sure You Have Admin or Send Message Permission In Target Channel/Group."
    )

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# PINNED BUTTON HANDLER
async def pinned_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    chats = [
        "Channel One",
        "Channel Two",
        "Channel Three",
        "Channel Four",
        "Channel Five",
        "Channel Six",
        "Channel Seven",
        "Channel Eight",
        "Channel Nine",
        "Channel Ten",
        "Channel Eleven",
        "Channel Twelve",
        "Channel Thirteen",
        "Channel Fourteen",
        "Channel Fifteen"
    ]

    text = "🎯 Select the Number Below to Set Your Target\n\n"

    for i, c in enumerate(chats, 1):
        text += f"{i}. {c}\n"

    keyboard = []
    row = []

    for i in range(1, len(chats)+1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"settarget_{i}"))

        if len(row) == 5:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
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
    app.add_handler(CommandHandler("target", target_ui))

    app.add_handler(CallbackQueryHandler(panel))
    app.add_handler(CallbackQueryHandler(pinned_handler, pattern="pinned"))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
