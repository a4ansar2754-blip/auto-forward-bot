import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from userbot_manager import login_user
from engine import start_engine, stop_engine, running
from chat_picker import get_user_chats, get_chat
from config_manager import get_config, save_config

BOT_TOKEN = os.getenv("BOT_TOKEN")

login_state = {}
phone_data = {}
mode_state = {}


# ---------------- PANEL ---------------- #

def main_panel():

    keyboard = [

        [InlineKeyboardButton("🔑 Login", callback_data="login")],

        [InlineKeyboardButton("📥 Add Sources", callback_data="addsrc")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="addtgt")],

        [InlineKeyboardButton("📌 Show Chats", callback_data="showchats")],

        [InlineKeyboardButton("🚀 Start Forward", callback_data="start")],
        [InlineKeyboardButton("⛔ Stop Forward", callback_data="stop")],

        [InlineKeyboardButton("📊 Dashboard", callback_data="dash")]
    ]

    return InlineKeyboardMarkup(keyboard)


# ---------------- CHAT BUTTONS ---------------- #

def chat_buttons():

    rows = []
    num = 1

    for i in range(3):

        row = []

        for j in range(5):

            row.append(
                InlineKeyboardButton(
                    str(num),
                    callback_data=f"chat_{num}"
                )
            )

            num += 1

        rows.append(row)

    return InlineKeyboardMarkup(rows)


# ---------------- START ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🚀 AUTO FORWARD PANEL",
        reply_markup=main_panel()
    )


# ---------------- LOGIN COMMAND ---------------- #

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id

    login_state[user] = "PHONE"

    await update.message.reply_text(
        "Send phone number\nExample:\n+919876543210"
    )


# ---------------- LOGIN FLOW (OTP FIXED) ---------------- #

async def login_flow(update, context):

    user = update.effective_user.id
    text = update.message.text

    if user not in login_state:
        return

    state = login_state[user]

    # STEP 1 : PHONE NUMBER
    if state == "PHONE":

        phone_data[user] = text

        await update.message.reply_text(
            "📡 Sending OTP...\nPlease wait..."
        )

        r = await login_user(user, phone=text)

        if r == "CODE":

            login_state[user] = "OTP"

            await update.message.reply_text(
                "📲 OTP Sent\n\nSend OTP now"
            )

        else:

            await update.message.reply_text(
                "❌ Failed to send OTP. Try again."
            )

    # STEP 2 : OTP
    elif state == "OTP":

        r = await login_user(user, code=text)

        if r == "SUCCESS":

            login_state.pop(user, None)
            phone_data.pop(user, None)

            await update.message.reply_text(
                "✅ LOGIN SUCCESS\n\nSession saved.\nYou will not need to login again."
            )

        else:

            await update.message.reply_text(
                "❌ OTP Wrong. Try again."
            )

        


# ---------------- BUTTON HANDLER ---------------- #

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user.id
    data = query.data

    if data == "login":

        login_state[user] = "PHONE"

        await query.message.reply_text(
            "Send phone number\nExample:\n+919876543210"
        )

    elif data == "addsrc":

        mode_state[user] = "SOURCE"

        await query.message.reply_text(
            "Select SOURCE from chats"
        )

    elif data == "addtgt":

        mode_state[user] = "TARGET"

        await query.message.reply_text(
            "Select TARGET from chats"
        )

    elif data == "showchats":

        chats = await get_user_chats(user)

        text = "📋 SELECT CHAT\n\n"

        for i, chat in enumerate(chats, start=1):
            text += f"{i}. {chat.name}\n"

        await query.message.reply_text(
            text,
            reply_markup=chat_buttons()
        )

    elif data.startswith("chat_"):

        index = int(data.split("_")[1]) - 1

        chat_id = get_chat(user, index)

        config = get_config(user)

        if mode_state.get(user) == "SOURCE":

            if chat_id not in config["sources"]:

                config["sources"].append(chat_id)

                await query.message.reply_text(
                    "✅ SOURCE ADDED"
                )

        elif mode_state.get(user) == "TARGET":

            if chat_id not in config["targets"]:

                config["targets"].append(chat_id)

                await query.message.reply_text(
                    "✅ TARGET ADDED"
                )

        save_config(user, config)

    elif data == "start":

        await start_engine(user)

        await query.message.reply_text(
            "🚀 Forward Started"
        )

    elif data == "stop":

        await stop_engine(user)

        await query.message.reply_text(
            "⛔ Forward Stopped"
        )

    elif data == "dash":

        config = get_config(user)

        status = "🟢 RUNNING" if user in running else "🔴 STOPPED"

        text = f"""
📊 DASHBOARD

Sources : {len(config['sources'])}
Targets : {len(config['targets'])}

Status : {status}
"""

        await query.message.reply_text(text)


# ---------------- MAIN ---------------- #

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))

    app.add_handler(CallbackQueryHandler(buttons))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, login_flow)
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
