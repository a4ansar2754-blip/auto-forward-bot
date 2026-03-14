import os
import json
from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient("userbot", API_ID, API_HASH)

# message mapping for reply/edit/delete sync
msg_map = {}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"sources": {}, "targets": {}, "settings": {}}

    with open(CONFIG_FILE) as f:
        return json.load(f)


# ---------------- START USERBOT ----------------

async def start_userbot():

    await client.start(string_session=STRING_SESSION)

    print("USERBOT STARTED")

    # ---------------- NORMAL MESSAGE ----------------

    @client.on(events.NewMessage)
    async def forward_handler(event):

        data = load_config()

        sources = data.get("sources", {})
        targets = data.get("targets", {})

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        for target_id in targets.keys():

            try:

                reply_to = None

                if event.message.is_reply:
                    reply_id = event.message.reply_to_msg_id
                    reply_to = msg_map.get(reply_id, {}).get(target_id)

                if event.message.media:

                    sent = await client.send_file(
                        int(target_id),
                        event.message.media,
                        caption=event.message.text,
                        reply_to=reply_to
                    )

                else:

                    sent = await client.send_message(
                        int(target_id),
                        event.message.text,
                        reply_to=reply_to,
                        link_preview=False
                    )

                msg_map.setdefault(event.message.id, {})[target_id] = sent.id

            except Exception as e:
                print("Forward error:", e)


    # ---------------- ALBUM FORWARD ----------------

    @client.on(events.Album)
    async def album_forward(event):

        data = load_config()

        sources = data.get("sources", {})
        targets = data.get("targets", {})

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        media_files = []
        caption = ""

        for msg in event.messages:

            if msg.media:
                media_files.append(msg.media)

            if msg.text and caption == "":
                caption = msg.text

        for target_id in targets.keys():

            try:

                sent = await client.send_file(
                    int(target_id),
                    media_files,
                    caption=caption
                )

                for i, msg in enumerate(event.messages):
                    msg_map.setdefault(msg.id, {})[target_id] = sent[i].id

            except Exception as e:
                print("Album error:", e)


    # ---------------- DELETE SYNC ----------------

    @client.on(events.MessageDeleted)
    async def delete_sync(event):

        data = load_config()
        targets = data.get("targets", {})

        for msg_id in event.deleted_ids:

            if msg_id in msg_map:

                for target_id, target_msg in msg_map[msg_id].items():

                    try:
                        await client.delete_messages(int(target_id), target_msg)
                    except:
                        pass


    # ---------------- EDIT SYNC ----------------

    @client.on(events.MessageEdited)
    async def edit_sync(event):

        msg_id = event.message.id

        if msg_id not in msg_map:
            return

        for target_id, target_msg in msg_map[msg_id].items():

            try:

                await client.edit_message(
                    int(target_id),
                    target_msg,
                    event.message.text
                )

            except:
                pass


    await client.run_until_disconnected()
