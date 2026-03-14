import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config_manager import get_config, save_config
from admin_manager import is_admin

BOT_TOKEN = os.getenv("BOT_TOKEN")


# ---------------- START PANEL ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="add_source")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="add_target")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")]
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PANEL\nChoose option 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- DASHBOARD ---------------- #

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    sources = data["sources"]
    targets = data["targets"]
    s = data["settings"]

    src_text = "\n".join([f"• {v}" for v in sources.values()]) or "None"
    tgt_text = "\n".join([f"• {v}" for v in targets.values()]) or "None"

    text = f"""
📊 BOT DASHBOARD

📥 SOURCES
{src_text}

🎯 TARGETS
{tgt_text}

⚙ SETTINGS

Forward : {"🟢" if s["forward"] else "🔴"}
Media : {"🟢" if s["media"] else "🔴"}
Remove Links : {"🟢" if s["remove_links"] else "🔴"}
Remove Username : {"🟢" if s["remove_username"] else "🔴"}
Auto Delete : {"🟢" if s["auto_delete"] else "🔴"}

Blacklist Words : {len(s["blacklist"])}
Replace Link : {s["replace_link"] or "None"}
"""

    await update.message.reply_text(text)


# ---------------- SOURCE LIST ---------------- #

async def sources(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    text = "📥 SOURCE CHANNELS\n\n"

    for i, v in enumerate(data["sources"].values(), 1):
        text += f"{i}. {v}\n"

    await update.message.reply_text(text)


# ---------------- TARGET LIST ---------------- #

async def targets(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    text = "🎯 TARGET CHANNELS\n\n"

    for i, v in enumerate(data["targets"].values(), 1):
        text += f"{i}. {v}\n"

    await update.message.reply_text(text)


# ---------------- REMOVE SOURCE ---------------- #

async def remove_source(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    if not context.args:
        await update.message.reply_text("Usage:\n/remove_source 1")
        return

    index = int(context.args[0]) - 1

    keys = list(data["sources"].keys())

    if index >= len(keys):
        await update.message.reply_text("Invalid source number")
        return

    removed = data["sources"].pop(keys[index])

    save_config(user, data)

    await update.message.reply_text(f"❌ Source removed\n{removed}")


# ---------------- REMOVE TARGET ---------------- #

async def remove_target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    if not context.args:
        await update.message.reply_text("Usage:\n/remove_target 1")
        return

    index = int(context.args[0]) - 1

    keys = list(data["targets"].keys())

    if index >= len(keys):
        await update.message.reply_text("Invalid target number")
        return

    removed = data["targets"].pop(keys[index])

    save_config(user, data)

    await update.message.reply_text(f"❌ Target removed\n{removed}")


# ---------------- SETTINGS ---------------- #

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    s = data["settings"]

    text = f"""
⚙ BOT SETTINGS

Forward : {"🟢 ON" if s["forward"] else "🔴 OFF"}
Media : {"🟢 ON" if s["media"] else "🔴 OFF"}
Remove Links : {"🟢 ON" if s["remove_links"] else "🔴 OFF"}
Remove Username : {"🟢 ON" if s["remove_username"] else "🔴 OFF"}
Auto Delete : {"🟢 ON" if s["auto_delete"] else "🔴 OFF"}
"""

    await update.message.reply_text(text)


# ---------------- ADMIN PANEL ---------------- #

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id

    if not is_admin(user):
        return

    total = len(os.listdir("configs"))

    await update.message.reply_text(
        f"👑 ADMIN PANEL\n\nTotal Users : {total}"
    )


# ---------------- MAIN ---------------- #

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("sources", sources))
    app.add_handler(CommandHandler("targets", targets))
    app.add_handler(CommandHandler("remove_source", remove_source))
    app.add_handler(CommandHandler("remove_target", remove_target))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CommandHandler("users", users))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
