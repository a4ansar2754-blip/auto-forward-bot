from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os
import json

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sources": [], "targets": []}

    with open(CONFIG_FILE) as f:
        return json.load(f)


async def start_userbot():

    await client.start()

    print("USERBOT STARTED")


    @client.on(events.NewMessage)
    async def handler(event):

        data = load_config()

        source_list = data["sources"]
        target_list = data["targets"]

        chat_id = str(event.chat_id)

        if chat_id in source_list:

            for target in target_list:

                try:
                    await client.forward_messages(
                        int(target),
                        event.message
                    )

                except Exception as e:
                    print("Forward Error:", e)


    await client.run_until_disconnected()
