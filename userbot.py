import os
import json
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient("userbot", API_ID, API_HASH)

message_map = {}


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


async def start_userbot():

    await client.start(string_session=STRING_SESSION)

    print("USERBOT STARTED")

    @client.on(events.NewMessage)
    async def handler(event):

        data = load_config()

        sources = data["sources"]
        targets = data["targets"]

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        for target_id in targets.keys():

            if event.message.media:

                sent = await client.send_file(
                    int(target_id),
                    event.message.media,
                    caption=event.message.text
                )

            else:

                sent = await client.send_message(
                    int(target_id),
                    event.message.text
                )

            message_map.setdefault(event.message.id, {})[target_id] = sent.id


    # ---------------- DELETE SYNC ----------------

    @client.on(events.MessageDeleted)
    async def delete_handler(event):

        for msg_id in event.deleted_ids:

            if msg_id in message_map:

                for target_id, target_msg in message_map[msg_id].items():

                    try:
                        await client.delete_messages(int(target_id), target_msg)
                    except:
                        pass


    # ---------------- EDIT SYNC ----------------

    @client.on(events.MessageEdited)
    async def edit_handler(event):

        msg_id = event.message.id

        if msg_id in message_map:

            for target_id, target_msg in message_map[msg_id].items():

                try:

                    await client.edit_message(
                        int(target_id),
                        target_msg,
                        event.message.text
                    )

                except:
                    pass


    await client.run_until_disconnected()
