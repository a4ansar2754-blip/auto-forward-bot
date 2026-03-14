import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config_manager import get_config, save_config
from userbot_manager import login_user, clients

BOT_TOKEN = os.getenv("BOT_TOKEN")

chat_cache = {}
mode = {}
login_state = {}


# ---------------- START PANEL ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("🗑 Remove Sources", callback_data="remove_sources")],
        [InlineKeyboardButton("❌ Remove Targets", callback_data="remove_targets")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PRO PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------- LOGIN COMMAND ---------------- #

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    login_state[user] = "PHONE"

    await update.message.reply_text(
        "📱 Send your phone number\nExample:\n+919876543210"
    )


# ---------------- LOGIN FLOW ---------------- #

async def login_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in login_state:
        return

    text = update.message.text

    state = login_state[user]

    if state == "PHONE":

        login_state[user] = {
            "step": "CODE",
            "phone": text
        }

        r = await login_user(user, text)

        if r == "CODE":

            await update.message.reply_text(
                "📩 OTP sent\nSend OTP code"
            )

    elif isinstance(state, dict):

        phone = state["phone"]

        r = await login_user(user, phone, code=text)

        if r == "PASSWORD":

            login_state[user]["step"] = "PASSWORD"

            await update.message.reply_text(
                "🔐 Send 2FA password"
            )

        elif r == "SUCCESS":

            login_state.pop(user)

            await update.message.reply_text(
                "✅ Login successful\nUserbot started"
            )


# ---------------- PANEL ---------------- #

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if query.data == "sources":

        mode[user] = "source"

        kb = [[InlineKeyboardButton("📌 Show Chats", callback_data="fetch")]]

        await query.message.reply_text(
            "📥 Select SOURCE channel",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif query.data == "targets":

        mode[user] = "target"

        kb = [[InlineKeyboardButton("📌 Show Chats", callback_data="fetch")]]

        await query.message.reply_text(
            "🎯 Select TARGET channel",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif query.data == "dashboard":

        await dashboard(query)


# ---------------- FETCH CHATS ---------------- #

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if user not in clients:

        await query.message.reply_text("❌ Login required\nUse /login first")
        return

    client = clients[user]

    dialogs = await client.get_dialogs()

    chats = dialogs[:15]

    chat_cache[user] = chats

    txt = "📋 SELECT CHAT\n\n"

    for i, c in enumerate(chats, 1):
        txt += f"{i}. {c.name}\n"

    btn = []
    row = []

    for i in range(1, len(chats) + 1):

        row.append(
            InlineKeyboardButton(str(i), callback_data=f"add_{i}")
        )

        if len(row) == 5:
            btn.append(row)
            row = []

    if row:
        btn.append(row)

    await query.message.reply_text(
        txt,
        reply_markup=InlineKeyboardMarkup(btn),
    )


# ---------------- ADD CHAT ---------------- #

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    index = int(query.data.split("_")[1]) - 1

    chats = chat_cache[user]

    chat = chats[index]

    cid = str(chat.id)
    name = chat.name

    data = get_config(user)

    if mode[user] == "source":

        if cid in data["sources"]:

            await query.message.reply_text(
                f"❌ Already SOURCE\n{name}"
            )
            return

        data["sources"][cid] = name

        await query.message.reply_text(
            f"✅ SOURCE ADDED\n{name}"
        )

    elif mode[user] == "target":

        if cid in data["targets"]:

            await query.message.reply_text(
                f"❌ Already TARGET\n{name}"
            )
            return

        data["targets"][cid] = name

        await query.message.reply_text(
            f"🎯 TARGET ADDED\n{name}"
        )

    save_config(user, data)


# ---------------- DASHBOARD ---------------- #

async def dashboard(query):

    user = query.from_user.id

    data = get_config(user)

    txt = f"""
📊 BOT DASHBOARD

📥 Sources : {len(data["sources"])}
🎯 Targets : {len(data["targets"])}
"""

    await query.message.reply_text(txt)


# ---------------- MAIN ---------------- #

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))

    app.add_handler(MessageHandler(filters.TEXT, login_flow))

    app.add_handler(CallbackQueryHandler(panel))
    app.add_handler(CallbackQueryHandler(fetch, pattern="fetch"))
    app.add_handler(CallbackQueryHandler(add, pattern="add_"))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
