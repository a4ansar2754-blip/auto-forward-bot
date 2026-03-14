import os
import json
import re
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"
SETTINGS_FILE = "settings.json"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

msg_map = {}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sources": {}, "targets": {}}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {}
    with open(SETTINGS_FILE) as f:
        return json.load(f)


def clean_text(text, settings):

    if not text:
        return text

    if settings.get("remove_links"):
        text = re.sub(r"http\S+", "", text)

    if settings.get("remove_username"):
        text = re.sub(r"@\w+", "", text)

    return text


async def send_copy(message, target, settings, reply_to=None):

    text = clean_text(message.text, settings)

    if message.media and settings.get("media"):

        file = await message.download_media()

        sent = await client.send_file(
            target,
            file,
            caption=text,
            reply_to=reply_to,
            link_preview=settings.get("preview")
        )

    else:

        sent = await client.send_message(
            target,
            text,
            reply_to=reply_to,
            link_preview=settings.get("preview")
        )

    if settings.get("auto_delete"):

        await asyncio.sleep(settings.get("auto_delete_time", 30))
        await sent.delete()

    return sent.id


async def start_userbot():

    await client.start()

    print("USERBOT STARTED")

    @client.on(events.NewMessage)
    async def handler(event):

        config = load_config()
        settings = load_settings()

        if not settings.get("forward", True):
            return

        sources = config["sources"]
        targets = config["targets"]

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        message = event.message

        if settings.get("blacklist"):
            for word in settings["blacklist"]:
                if word.lower() in (message.text or "").lower():
                    return

        reply_to = None

        if message.reply_to_msg_id:

            key = (event.chat_id, message.reply_to_msg_id)
            reply_to = msg_map.get(key)

        for target_id in targets.keys():

            sent_id = await send_copy(
                message,
                int(target_id),
                settings,
                reply_to
            )

            msg_map[(event.chat_id, message.id)] = sent_id

    await client.run_until_disconnected()
