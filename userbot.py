import os
import json
import re
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient("userbot", API_ID, API_HASH)

message_map = {}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sources": {}, "targets": {}, "settings": {}}

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


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

            sent = await client.send_file(
                target,
                file,
                caption=text
            )

        else:

            sent = await client.send_message(
                target,
                text,
                link_preview=False
            )

        return sent.id

    except Exception as e:
        print("Forward error:", e)


async def start_userbot():

    await client.start(string_session=STRING_SESSION)

    print("USERBOT STARTED")

    @client.on(events.NewMessage)
    async def handler(event):

        data = load_config()

        sources = data["sources"]
        targets = data["targets"]
        settings = data["settings"]

        if not settings["forward"]:
            return

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        text = event.message.text or ""

        for word in settings["blacklist"]:
            if word.lower() in text.lower():
                return

        for target_id in targets.keys():

            sent_id = await copy_message(
                event.message,
                int(target_id),
                settings
            )

            if sent_id:

                message_map.setdefault(event.message.id, {})[
                    target_id
                ] = sent_id


    @client.on(events.MessageDeleted)
    async def delete_handler(event):

        data = load_config()
        targets = data["targets"]
        settings = data["settings"]

        if not settings["auto_delete"]:
            return

        for msg_id in event.deleted_ids:

            if msg_id in message_map:

                for target_id, target_msg in message_map[msg_id].items():

                    try:
                        await client.delete_messages(
                            int(target_id),
                            target_msg
                        )
                    except:
                        pass

    await client.run_until_disconnected()
