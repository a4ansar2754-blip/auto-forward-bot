import os
import json
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
ApplicationBuilder,
CommandHandler,
CallbackQueryHandler,
ContextTypes
)

from userbot import client, start_userbot

BOT_TOKEN = os.getenv("BOT_TOKEN")
CONFIG_FILE = "config.json"

chat_list = []
mode = None


def load_config():

    if not os.path.exists(CONFIG_FILE):

        with open(CONFIG_FILE,"w") as f:

            json.dump({

                "sources":{},
                "targets":{},
                "settings":{
                    "forward":True,
                    "media":True,
                    "remove_links":False,
                    "remove_username":False,
                    "auto_delete":False,
                    "blacklist":[],
                    "replace_link":""
                }

            },f)

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):

    with open(CONFIG_FILE,"w") as f:
        json.dump(data,f,indent=4)


def icon(v):
    return "🟢" if v else "🔴"


# ---------------- START PANEL ----------------

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    keyboard=[

        [InlineKeyboardButton("📥 Add Sources",callback_data="sources")],
        [InlineKeyboardButton("🎯 Add Targets",callback_data="targets")],
        [InlineKeyboardButton("📊 Dashboard",callback_data="dashboard")]

    ]

    await update.message.reply_text(

        "🚀 AUTO FORWARD PANEL\n\nChoose option 👇",

        reply_markup=InlineKeyboardMarkup(keyboard)

    )


# ---------------- PANEL ----------------

async def panel(update:Update,context:ContextTypes.DEFAULT_TYPE):

    global mode

    query=update.callback_query
    await query.answer()

    if query.data=="sources":

        mode="source"

        kb=[[InlineKeyboardButton("📌 Show Chats",callback_data="fetch")]]

        await query.message.reply_text(

            "📥 Select SOURCE channel",

            reply_markup=InlineKeyboardMarkup(kb)

        )


    elif query.data=="targets":

        mode="target"

        kb=[[InlineKeyboardButton("📌 Show Chats",callback_data="fetch")]]

        await query.message.reply_text(

            "🎯 Select TARGET channel",

            reply_markup=InlineKeyboardMarkup(kb)

        )


    elif query.data=="dashboard":

        data=load_config()
        s=data["settings"]

        text="📊 BOT DASHBOARD\n\n"

        text+="📥 SOURCES\n"

        if data["sources"]:
            for x in data["sources"].values():
                text+=f"• {x}\n"
        else:
            text+="None\n"

        text+="\n🎯 TARGETS\n"

        if data["targets"]:
            for x in data["targets"].values():
                text+=f"• {x}\n"
        else:
            text+="None\n"

        text+=f"""

⚙ SETTINGS

Forward : {icon(s["forward"])}
Media : {icon(s["media"])}
Remove Links : {icon(s["remove_links"])}
Remove Username : {icon(s["remove_username"])}
Auto Delete : {icon(s["auto_delete"])}

Blacklist Words : {len(s["blacklist"])}
Replace Link : {s["replace_link"] or "None"}
"""

        await query.message.reply_text(text)


# ---------------- FETCH CHATS ----------------

async def fetch(update:Update,context:ContextTypes.DEFAULT_TYPE):

    global chat_list

    query=update.callback_query
    await query.answer()

    dialogs=await client.get_dialogs()

    chat_list=dialogs[:15]

    txt="📋 SELECT CHAT\n\n"

    for i,c in enumerate(chat_list,1):
        txt+=f"{i}. {c.name}\n"

    btn=[]
    row=[]

    for i in range(1,len(chat_list)+1):

        row.append(InlineKeyboardButton(str(i),callback_data=f"add_{i}"))

        if len(row)==5:
            btn.append(row)
            row=[]

    if row:
        btn.append(row)

    await query.message.reply_text(

        txt,

        reply_markup=InlineKeyboardMarkup(btn)

    )


# ---------------- ADD CHAT ----------------

async def add(update:Update,context:ContextTypes.DEFAULT_TYPE):

    global mode

    query=update.callback_query
    await query.answer()

    index=int(query.data.split("_")[1])-1

    if index>=len(chat_list):

        await query.message.reply_text("❌ Invalid selection")
        return

    chat=chat_list[index]

    cid=str(chat.id)
    name=chat.name

    data=load_config()

    if mode=="source":

        if cid in data["sources"]:

            await query.message.reply_text(
                f"❌ Already added as SOURCE\n📥 {name}"
            )

            return

        data["sources"][cid]=name

        await query.message.reply_text(
            f"✅ SOURCE ADDED\n📥 {name}"
        )


    elif mode=="target":

        if cid in data["targets"]:

            await query.message.reply_text(
                f"❌ Already added as TARGET\n🎯 {name}"
            )

            return

        data["targets"][cid]=name

        await query.message.reply_text(
            f"✅ TARGET ADDED\n🎯 {name}"
        )


    save_config(data)


# ---------------- USERBOT START ----------------

async def startup(app):

    asyncio.create_task(start_userbot())


# ---------------- MAIN ----------------

def main():

    app=ApplicationBuilder().token(BOT_TOKEN).post_init(startup).build()

    app.add_handler(CommandHandler("start",start))

    app.add_handler(
        CallbackQueryHandler(panel,pattern="^(sources|targets|dashboard)$")
    )

    app.add_handler(
        CallbackQueryHandler(fetch,pattern="^fetch$")
    )

    app.add_handler(
        CallbackQueryHandler(add,pattern=r"^add_\d+$")
    )

    print("BOT STARTED")

    app.run_polling()


if __name__=="__main__":

    main()
