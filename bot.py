import os
import json
import asyncio

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

from userbot import start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")

CONFIG_FILE = "config.json"


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🚀 AUTO FORWARD PANEL\n\nUse commands menu"
    )


async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    text = "📊 DASHBOARD\n\n"

    text += "📥 SOURCES\n"

    for s in data["sources"].values():
        text += f"• {s}\n"

    text += "\n🎯 TARGETS\n"

    for t in data["targets"].values():
        text += f"• {t}\n"

    await update.message.reply_text(text)


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

    await update.message.reply_text("📸 Media forwarding ON")


async def media_off(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["media"] = False

    save_config(data)

    await update.message.reply_text("📸 Media forwarding OFF")


async def links_on(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["remove_links"] = True

    save_config(data)

    await update.message.reply_text("🔗 Links removed")


async def links_off(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["remove_links"] = False

    save_config(data)

    await update.message.reply_text("🔗 Links allowed")


async def username_on(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["remove_username"] = True

    save_config(data)

    await update.message.reply_text("👤 Username removed")


async def username_off(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["remove_username"] = False

    save_config(data)

    await update.message.reply_text("👤 Username allowed")


async def autodelete_on(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["auto_delete"] = True

    save_config(data)

    await update.message.reply_text("🗑 Auto delete ON")


async def autodelete_off(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    data["settings"]["auto_delete"] = False

    save_config(data)

    await update.message.reply_text("🗑 Auto delete OFF")


async def blacklist_add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    word = context.args[0]

    data = load_config()

    data["settings"]["blacklist"].append(word)

    save_config(data)

    await update.message.reply_text(f"🚫 Blacklist added: {word}")


async def blacklist_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):

    word = context.args[0]

    data = load_config()

    data["settings"]["blacklist"].remove(word)

    save_config(data)

    await update.message.reply_text(f"✅ Removed blacklist: {word}")


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()

    s = data["settings"]

    text = f"""
⚙ SETTINGS

Forward: {s["forward"]}
Media: {s["media"]}
Remove Links: {s["remove_links"]}
Remove Username: {s["remove_username"]}
Auto Delete: {s["auto_delete"]}
Blacklist: {s["blacklist"]}
"""

    await update.message.reply_text(text)


async def on_startup(app):

    asyncio.create_task(start_userbot())


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(on_startup).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
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
    app.add_handler(CommandHandler("blacklist_add", blacklist_add))
    app.add_handler(CommandHandler("blacklist_remove", blacklist_remove))
    app.add_handler(CommandHandler("settings", settings))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
