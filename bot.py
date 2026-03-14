import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config_manager import get_config, save_config
from admin_manager import is_admin

BOT_TOKEN = os.getenv("BOT_TOKEN")


# ---------------- START PANEL ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Source", callback_data="add_source")],
        [InlineKeyboardButton("🎯 Add Target", callback_data="add_target")],
        [InlineKeyboardButton("🗑 Remove Source", callback_data="remove_source")],
        [InlineKeyboardButton("❌ Remove Target", callback_data="remove_target")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")]
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PRO PANEL\nChoose option 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- DASHBOARD ---------------- #

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    sources = data["sources"]
    targets = data["targets"]
    s = data["settings"]

    src = "\n".join([f"• {v}" for v in sources.values()]) or "None"
    tgt = "\n".join([f"• {v}" for v in targets.values()]) or "None"

    text = f"""
📊 BOT DASHBOARD

📥 SOURCES
{src}

🎯 TARGETS
{tgt}

⚙ SETTINGS

Forward : {"🟢" if s["forward"] else "🔴"}
Media : {"🟢" if s["media"] else "🔴"}
Remove Links : {"🟢" if s["remove_links"] else "🔴"}
Remove Username : {"🟢" if s["remove_username"] else "🔴"}
Auto Delete : {"🟢" if s["auto_delete"] else "🔴"}

Blacklist Words : {len(s["blacklist"])}
Replace Link : {s["replace_link"] or "None"}
"""

    await update.callback_query.message.reply_text(text)


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

    await update.callback_query.message.reply_text(text)


# ---------------- REMOVE SOURCE ---------------- #

async def remove_source(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    text = "🗑 SOURCE LIST\n\n"

    for i, v in enumerate(data["sources"].values(), 1):
        text += f"{i}. {v}\n"

    text += "\nUse command:\n/remove_source number"

    await update.callback_query.message.reply_text(text)


# ---------------- REMOVE TARGET ---------------- #

async def remove_target(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    data = get_config(user)

    text = "❌ TARGET LIST\n\n"

    for i, v in enumerate(data["targets"].values(), 1):
        text += f"{i}. {v}\n"

    text += "\nUse command:\n/remove_target number"

    await update.callback_query.message.reply_text(text)


# ---------------- PANEL HANDLER ---------------- #

async def panel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "dashboard":
        await dashboard(update, context)

    elif data == "settings":
        await settings(update, context)

    elif data == "remove_source":
        await remove_source(update, context)

    elif data == "remove_target":
        await remove_target(update, context)

    elif data == "add_source":
        await query.message.reply_text(
            "📥 Send channel ID to add source\nExample:\n-100123456789"
        )

    elif data == "add_target":
        await query.message.reply_text(
            "🎯 Send channel ID to add target\nExample:\n-100123456789"
        )


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
    app.add_handler(CommandHandler("users", users))

    app.add_handler(CallbackQueryHandler(panel_handler))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
