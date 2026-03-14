import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

from config_manager import get_config, save_config
from userbot_manager import clients

BOT_TOKEN = os.getenv("BOT_TOKEN")

chat_cache = {}
mode = {}


# ---------------- START PANEL ---------------- #

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Add Sources", callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets", callback_data="targets")],
        [InlineKeyboardButton("🗑 Remove Sources", callback_data="remove_sources")],
        [InlineKeyboardButton("❌ Remove Targets", callback_data="remove_targets")],
        [InlineKeyboardButton("⚙ Settings", callback_data="settings")],
        [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")]
    ]

    await update.message.reply_text(
        "🚀 AUTO FORWARD PRO PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
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
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "targets":

        mode[user] = "target"

        kb = [[InlineKeyboardButton("📌 Show Chats", callback_data="fetch")]]

        await query.message.reply_text(
            "🎯 Select TARGET channel",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "remove_sources":

        data = get_config(user)

        txt = "🗑 SOURCE LIST\n\n"

        for i, v in enumerate(data["sources"].values(), 1):
            txt += f"{i}. {v}\n"

        txt += "\nUse command:\n/remove_source number"

        await query.message.reply_text(txt)

    elif query.data == "remove_targets":

        data = get_config(user)

        txt = "❌ TARGET LIST\n\n"

        for i, v in enumerate(data["targets"].values(), 1):
            txt += f"{i}. {v}\n"

        txt += "\nUse command:\n/remove_target number"

        await query.message.reply_text(txt)

    elif query.data == "settings":

        await settings_panel(query)

    elif query.data.startswith("toggle_"):

        await toggle_setting(query)

    elif query.data == "dashboard":

        await dashboard(query)


# ---------------- SETTINGS PANEL ---------------- #

async def settings_panel(query):

    user = query.from_user.id

    data = get_config(user)

    s = data["settings"]

    keyboard = [
        [
            InlineKeyboardButton(
                f"Forward {'🟢' if s['forward'] else '🔴'}",
                callback_data="toggle_forward"
            )
        ],
        [
            InlineKeyboardButton(
                f"Media {'🟢' if s['media'] else '🔴'}",
                callback_data="toggle_media"
            )
        ],
        [
            InlineKeyboardButton(
                f"Remove Links {'🟢' if s['remove_links'] else '🔴'}",
                callback_data="toggle_links"
            )
        ],
        [
            InlineKeyboardButton(
                f"Remove Username {'🟢' if s['remove_username'] else '🔴'}",
                callback_data="toggle_username"
            )
        ],
        [
            InlineKeyboardButton(
                f"Auto Delete {'🟢' if s['auto_delete'] else '🔴'}",
                callback_data="toggle_delete"
            )
        ]
    ]

    await query.message.reply_text(
        "⚙ SETTINGS PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- TOGGLE SETTINGS ---------------- #

async def toggle_setting(query):

    user = query.from_user.id

    data = get_config(user)

    s = data["settings"]

    key = query.data.split("_")[1]

    if key == "forward":
        s["forward"] = not s["forward"]

    elif key == "media":
        s["media"] = not s["media"]

    elif key == "links":
        s["remove_links"] = not s["remove_links"]

    elif key == "username":
        s["remove_username"] = not s["remove_username"]

    elif key == "delete":
        s["auto_delete"] = not s["auto_delete"]

    save_config(user, data)

    await settings_panel(query)


# ---------------- DASHBOARD ---------------- #

async def dashboard(query):

    user = query.from_user.id

    data = get_config(user)

    s = data["settings"]

    txt = f"""
📊 BOT DASHBOARD

📥 Sources : {len(data["sources"])}
🎯 Targets : {len(data["targets"])}

⚙ Settings

Forward : {"🟢" if s["forward"] else "🔴"}
Media : {"🟢" if s["media"] else "🔴"}
Remove Links : {"🟢" if s["remove_links"] else "🔴"}
Remove Username : {"🟢" if s["remove_username"] else "🔴"}
Auto Delete : {"🟢" if s["auto_delete"] else "🔴"}
"""

    await query.message.reply_text(txt)


# ---------------- FETCH CHATS ---------------- #

async def fetch(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    if user not in clients:

        await query.message.reply_text("❌ Login required")
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
        reply_markup=InlineKeyboardMarkup(btn)
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


# ---------------- MAIN ---------------- #

def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(panel, pattern="sources|targets|remove_sources|remove_targets|settings|dashboard|toggle_"))

    app.add_handler(CallbackQueryHandler(fetch, pattern="fetch"))

    app.add_handler(CallbackQueryHandler(add, pattern="add_"))

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
