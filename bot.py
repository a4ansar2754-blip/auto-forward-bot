import os
import json
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from userbot import client, start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONFIG_FILE = "config.json"

chat_list = []
mode = None
waiting_blacklist = False
waiting_replace = False


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
                    "replace_link": "",
                    "auto_delete": False,
                    "blacklist": []
                }
            }, f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):

    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def icon(v):
    return "🟢" if v else "🔴"


# ---------- START PANEL ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------- PANEL ----------

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    if query.data == "sources":

        mode = "source"

        kb = [[InlineKeyboardButton("📌 I have pinned the chats", callback_data="fetch")]]

        await query.message.reply_text(
            "Add SOURCE channel",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "targets":

        mode = "target"

        kb = [[InlineKeyboardButton("📌 I have pinned the chats", callback_data="fetch")]]

        await query.message.reply_text(
            "Add TARGET channel",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "dashboard":

        data = load_config()
        s = data["settings"]

        text = f"""
⚙ BOT DASHBOARD

Forward: {icon(s["forward"])}
Media: {icon(s["media"])}
Remove Links: {icon(s["remove_links"])}
Remove Username: {icon(s["remove_username"])}
Auto Delete: {icon(s["auto_delete"])}

Blacklist: {len(s["blacklist"])} words
Replace Link: {s["replace_link"] or "None"}
"""

        await query.message.reply_text(text)


# ---------- FETCH CHATS ----------

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global chat_list

    query = update.callback_query
    await query.answer()

    dialogs = await client.get_dialogs()

    chat_list = dialogs[:15]

    txt = "Select chat\n\n"

    for i, c in enumerate(chat_list, 1):
        txt += f"{i}. {c.name}\n"

    btn = []
    row = []

    for i in range(1, len(chat_list) + 1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"add_{i}"))

        if len(row) == 5:
            btn.append(row)
            row = []

    if row:
        btn.append(row)

    await query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(btn))


# ---------- ADD CHAT ----------

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    index = int(query.data.split("_")[1]) - 1

    chat = chat_list[index]

    cid = str(chat.id)
    name = chat.name

    data = load_config()

    if mode == "source":

        if cid in data["sources"]:
            await query.message.reply_text("Already source")
            return

        data["sources"][cid] = name
        await query.message.reply_text(f"Added source {name}")

    elif mode == "target":

        if cid in data["targets"]:
            await query.message.reply_text("Already target")
            return

        data["targets"][cid] = name
        await query.message.reply_text(f"Added target {name}")

    save_config(data)


# ---------- BLACKLIST ----------

async def blacklist_add(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_blacklist

    waiting_blacklist = True

    await update.message.reply_text("Send words separated by comma")


async def replace_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_replace

    waiting_replace = True

    await update.message.reply_text("Send link to replace")


async def message_input(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global waiting_blacklist, waiting_replace

    data = load_config()

    if waiting_blacklist:

        words = [w.strip() for w in update.message.text.split(",")]

        data["settings"]["blacklist"] += words

        save_config(data)

        waiting_blacklist = False

        await update.message.reply_text("Blacklist saved")

    elif waiting_replace:

        data["settings"]["replace_link"] = update.message.text

        save_config(data)

        waiting_replace = False

        await update.message.reply_text("Replace link saved")


# ---------- USERBOT START ----------

async def startup(app):
    asyncio.create_task(start_userbot())


# ---------- MAIN ----------

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(startup).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CommandHandler("forward_on", forward_on))
    app.add_handler(CommandHandler("forward_off", forward_off))

    app.add_handler(CommandHandler("media_on", media_on))
    app.add_handler(CommandHandler("media_off", media_off))

    app.add_handler(CommandHandler("links_on", links_on))
    app.add_handler(CommandHandler("links_off", links_off))

    app.add_handler(CommandHandler("username_on", username_on))
    app.add_handler(CommandHandler("username_off", username_off))

    app.add_handler(CommandHandler("blacklist_add", blacklist_add))
    app.add_handler(CommandHandler("set_replace_link", replace_link))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_input))

    app.add_handler(CallbackQueryHandler(panel, pattern="sources|targets|dashboard"))
    app.add_handler(CallbackQueryHandler(fetch, pattern="fetch"))
    app.add_handler(CallbackQueryHandler(add, pattern=r"^add_\d+$"))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
