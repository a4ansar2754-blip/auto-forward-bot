import os
import json
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from userbot import client, start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONFIG_FILE = "config.json"

chat_list = []
mode = None


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def icon(v):
    return "🟢" if v else "🔴"


# ---------------- START PANEL ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("❌ Remove Sources", callback_data="remove_sources")],
        [InlineKeyboardButton("❌ Remove Targets", callback_data="remove_targets")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------- PANEL ----------------

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global mode

    query = update.callback_query
    await query.answer()

    if query.data == "sources":
        mode = "source"
        kb = [[InlineKeyboardButton("📌 Show Chats", callback_data="fetch")]]
        await query.message.reply_text(
            "📥 Select SOURCE channel",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif query.data == "targets":
        mode = "target"
        kb = [[InlineKeyboardButton("📌 Show Chats", callback_data="fetch")]]
        await query.message.reply_text(
            "🎯 Select TARGET channel",
            reply_markup=InlineKeyboardMarkup(kb),
        )

    elif query.data == "remove_sources":
        await remove_sources_ui(update)

    elif query.data == "remove_targets":
        await remove_targets_ui(update)

    elif query.data == "dashboard":
        await dashboard(update, context)


# ---------------- DASHBOARD ----------------

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = load_config()
    s = data["settings"]

    text = "📊 BOT DASHBOARD\n\n"

    text += "📥 SOURCES\n"
    if data["sources"]:
        for x in data["sources"].values():
            text += f"• {x}\n"
    else:
        text += "None\n"

    text += "\n🎯 TARGETS\n"
    if data["targets"]:
        for x in data["targets"].values():
            text += f"• {x}\n"
    else:
        text += "None\n"

    text += f"""

⚙ SETTINGS

Forward : {icon(s["forward"])}
Media : {icon(s["media"])}
Remove Links : {icon(s["remove_links"])}
Remove Username : {icon(s["remove_username"])}
Auto Delete : {icon(s["auto_delete"])}

Blacklist Words : {len(s["blacklist"])}
Replace Link : {s.get("replace_link") or "None"}
"""

    if update.callback_query:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)


# ---------------- FETCH CHATS ----------------

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global chat_list

    query = update.callback_query
    await query.answer()

    dialogs = await client.get_dialogs()
    chat_list = dialogs[:15]

    txt = "📋 SELECT CHAT\n\n"

    for i, c in enumerate(chat_list, 1):
        txt += f"{i}. {c.name}\n"

    buttons = []
    row = []

    for i in range(1, len(chat_list) + 1):

        row.append(InlineKeyboardButton(str(i), callback_data=f"add_{i}"))

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    await query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(buttons))


# ---------------- ADD CHAT ----------------

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
            await query.message.reply_text(f"❌ Already SOURCE\n{name}")
            return

        data["sources"][cid] = name
        await query.message.reply_text(f"✅ SOURCE ADDED\n{name}")

    elif mode == "target":

        if cid in data["targets"]:
            await query.message.reply_text(f"❌ Already TARGET\n{name}")
            return

        data["targets"][cid] = name
        await query.message.reply_text(f"✅ TARGET ADDED\n{name}")

    save_config(data)


# ---------------- REMOVE UI ----------------

async def remove_sources_ui(update):

    query = update.callback_query
    data = load_config()

    sources = list(data["sources"].items())

    if not sources:
        await query.message.reply_text("No sources added")
        return

    text = "❌ SELECT SOURCE TO REMOVE\n\n"

    buttons = []
    row = []

    for i, (cid, name) in enumerate(sources, 1):

        text += f"{i}. {name}\n"

        row.append(InlineKeyboardButton(str(i), callback_data=f"rs_{cid}"))

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("❌ Remove ALL", callback_data="rs_all")])

    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def remove_targets_ui(update):

    query = update.callback_query
    data = load_config()

    targets = list(data["targets"].items())

    if not targets:
        await query.message.reply_text("No targets added")
        return

    text = "❌ SELECT TARGET TO REMOVE\n\n"

    buttons = []
    row = []

    for i, (cid, name) in enumerate(targets, 1):

        text += f"{i}. {name}\n"

        row.append(InlineKeyboardButton(str(i), callback_data=f"rt_{cid}"))

        if len(row) == 5:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([InlineKeyboardButton("❌ Remove ALL", callback_data="rt_all")])

    await query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


async def remove_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = load_config()

    if query.data == "rs_all":
        data["sources"] = {}
        save_config(data)
        await query.message.reply_text("All sources removed")
        return

    if query.data == "rt_all":
        data["targets"] = {}
        save_config(data)
        await query.message.reply_text("All targets removed")
        return

    if query.data.startswith("rs_"):

        cid = query.data.replace("rs_", "")

        if cid in data["sources"]:

            name = data["sources"][cid]
            del data["sources"][cid]
            save_config(data)

            await query.message.reply_text(f"❌ SOURCE REMOVED\n{name}")

    if query.data.startswith("rt_"):

        cid = query.data.replace("rt_", "")

        if cid in data["targets"]:

            name = data["targets"][cid]
            del data["targets"][cid]
            save_config(data)

            await query.message.reply_text(f"❌ TARGET REMOVED\n{name}")


# ---------------- SETTINGS COMMANDS ----------------

async def set_toggle(update, key, value):

    data = load_config()
    data["settings"][key] = value
    save_config(data)

    await update.message.reply_text(f"{key} set to {value}")


async def forward_on(update, c): await set_toggle(update, "forward", True)
async def forward_off(update, c): await set_toggle(update, "forward", False)

async def media_on(update, c): await set_toggle(update, "media", True)
async def media_off(update, c): await set_toggle(update, "media", False)

async def links_on(update, c): await set_toggle(update, "remove_links", True)
async def links_off(update, c): await set_toggle(update, "remove_links", False)

async def username_on(update, c): await set_toggle(update, "remove_username", True)
async def username_off(update, c): await set_toggle(update, "remove_username", False)

async def autodelete_on(update, c): await set_toggle(update, "auto_delete", True)
async def autodelete_off(update, c): await set_toggle(update, "auto_delete", False)


async def blacklist_add(update, context):

    data = load_config()
    words = context.args

    data["settings"]["blacklist"].extend(words)

    save_config(data)

    await update.message.reply_text("Blacklist updated")


async def blacklist_remove(update, context):

    data = load_config()
    words = context.args

    data["settings"]["blacklist"] = [
        w for w in data["settings"]["blacklist"] if w not in words
    ]

    save_config(data)

    await update.message.reply_text("Blacklist updated")


# ---------------- REMOVE COMMAND ----------------

async def remove_source(update, context):

    data = load_config()

    cid = context.args[0]

    if cid in data["sources"]:

        del data["sources"][cid]
        save_config(data)

        await update.message.reply_text("Source removed")


async def remove_target(update, context):

    data = load_config()

    cid = context.args[0]

    if cid in data["targets"]:

        del data["targets"][cid]
        save_config(data)

        await update.message.reply_text("Target removed")


async def commands(update, context):

    await update.message.reply_text("Commands working")


# ---------------- START USERBOT ----------------

async def startup(app):

    asyncio.create_task(start_userbot())


# ---------------- MAIN ----------------

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(startup).build()

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

    app.add_handler(CommandHandler("remove_source", remove_source))
    app.add_handler(CommandHandler("remove_target", remove_target))
    app.add_handler(CommandHandler("commands", commands))

    app.add_handler(CallbackQueryHandler(panel, pattern="^(sources|targets|remove_sources|remove_targets|dashboard)$"))
    app.add_handler(CallbackQueryHandler(fetch, pattern="^fetch$"))
    app.add_handler(CallbackQueryHandler(add, pattern=r"^add_\d+$"))
    app.add_handler(CallbackQueryHandler(remove_handler, pattern="^(rs_|rt_|rs_all|rt_all)"))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
