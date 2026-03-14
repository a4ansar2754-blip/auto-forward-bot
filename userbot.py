import os
import json
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sources": {}, "targets": {}}

    with open(CONFIG_FILE) as f:
        return json.load(f)


async def copy_message(message, target):

    try:

        if message.text:
            await client.send_message(
                target,
                message.text,
                link_preview=False
            )

        elif message.media:

            file = await message.download_media()

            await client.send_file(
                target,
                file,
                caption=message.text if message.text else None
            )

    except Exception as e:
        print("Forward Error:", e)


async def start_userbot():

    await client.start()

    print("USERBOT STARTED")

    @client.on(events.NewMessage)
    async def handler(event):

        data = load_config()

        sources = data["sources"]
        targets = data["targets"]

        chat_id = str(event.chat_id)

        if chat_id in sources:

            for target_id in targets.keys():

                await copy_message(event.message, int(target_id))

    await client.run_until_disconnected()
