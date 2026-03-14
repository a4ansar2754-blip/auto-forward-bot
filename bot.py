import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from userbot_manager import login_user, clients
from config_manager import get_config, save_config

BOT_TOKEN = os.getenv("BOT_TOKEN")

login_state = {}
chat_cache = {}
mode = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    kb = [
        [InlineKeyboardButton("🔑 Login", callback_data="login")],
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("🗑 Remove Sources", callback_data="remove_sources")],
        [InlineKeyboardButton("❌ Remove Targets", callback_data="remove_targets")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PANEL",
        reply_markup=InlineKeyboardMarkup(kb)
    )

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if q.data == "login":

        login_state[user] = "PHONE"

        await q.message.reply_text("Send phone number\nExample:\n+919876543210")

    elif q.data in ["sources","targets"]:

        mode[user] = q.data

        await q.message.reply_text(
            "📋 Show chats",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Show Chats", callback_data="fetch")]]
            )
        )

    elif q.data == "dashboard":

        data = get_config(user)

        txt = f"""
📊 Dashboard

Sources: {len(data["sources"])}
Targets: {len(data["targets"])}
"""

        await q.message.reply_text(txt)

async def login_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user not in login_state:
        return

    text = update.message.text

    state = login_state[user]

    if state == "PHONE":

        login_state[user] = {"phone": text}

        r = await login_user(user, text)

        if r == "CODE":

            await update.message.reply_text("Send OTP")

    else:

        phone = state["phone"]

        r = await login_user(user, phone, code=text)

        if r == "SUCCESS":

            login_state.pop(user)

            await update.message.reply_text("✅ Login successful")

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if user not in clients:

        await q.message.reply_text("Login first")
        return

    client = clients[user]

    dialogs = await client.get_dialogs()

    chats = dialogs[:15]

    chat_cache[user] = chats

    text = "SELECT CHAT\n\n"

    for i,c in enumerate(chats,1):
        text += f"{i}. {c.name}\n"

    buttons = []
    row = []

    for i in range(1,len(chats)+1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"add_{i}"))

        if len(row)==5:
            buttons.append(row)
            row=[]

    if row:
        buttons.append(row)

    await q.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    idx = int(q.data.split("_")[1])-1

    chat = chat_cache[user][idx]

    data = get_config(user)

    if mode[user]=="sources":

        data["sources"][str(chat.id)] = chat.name
        await q.message.reply_text("Source added")

    else:

        data["targets"][str(chat.id)] = chat.name
        await q.message.reply_text("Target added")

    save_config(user,data)

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CallbackQueryHandler(panel))
    app.add_handler(CallbackQueryHandler(fetch,pattern="fetch"))
    app.add_handler(CallbackQueryHandler(add,pattern="add_"))
    app.add_handler(MessageHandler(filters.TEXT,login_flow))

    print("BOT STARTED")

    app.run_polling()

if __name__=="__main__":
    main()
