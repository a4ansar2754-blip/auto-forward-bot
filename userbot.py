import os
import json
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"
SETTINGS_FILE = "settings.json"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sources": {}, "targets": {}}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "forward": True,
            "hide_header": True,
            "media": True,
            "preview": True,
            "remove_links": False,
            "remove_username": True,
            "auto_delete": False,
            "blacklist": []
        }
    with open(SETTINGS_FILE) as f:
        return json.load(f)


def clean_text(text, settings):

    if not text:
        return text

    if settings["remove_links"]:
        text = re.sub(r"http\S+", "", text)

    if settings["remove_username"]:
        text = re.sub(r"@\w+", "", text)

    return text


async def copy_message(message, target, settings):

    try:

        text = clean_text(message.text, settings)

        if message.media and settings["media"]:

            file = await message.download_media()

            await client.send_file(
                target,
                file,
                caption=text,
                link_preview=settings["preview"]
            )

        else:

            await client.send_message(
                target,
                text,
                link_preview=settings["preview"]
            )

    except Exception as e:
        print("Forward Error:", e)


async def start_userbot():

    await client.start()

    print("USERBOT STARTED")

    @client.on(events.NewMessage)
    async def handler(event):

        config = load_config()
        settings = load_settings()

        if not settings["forward"]:
            return

        sources = config["sources"]
        targets = config["targets"]

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        message = event.message

        if settings["blacklist"]:
            for word in settings["blacklist"]:
                if word.lower() in (message.text or "").lower():
                    return

        for target_id in targets.keys():

            sent = await copy_message(message, int(target_id), settings)

    await client.run_until_disconnected()
