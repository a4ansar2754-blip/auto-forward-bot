import os
import json
import re

from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

msg_map = {}


def load():

    with open(CONFIG_FILE) as f:
        return json.load(f)


async def start_userbot():

    await client.start()

    print("USERBOT RUNNING")

    # NORMAL MESSAGE

    @client.on(events.NewMessage)

    async def forward_handler(event):

        data = load()

        sources = data["sources"]
        targets = data["targets"]
        settings = data["settings"]

        if not settings["forward"]:
            return

        cid = str(event.chat_id)

        if cid not in sources:
            return

        text = event.message.text or ""

        for word in settings["blacklist"]:

            if word.lower() in text.lower():
                return

        if settings["remove_username"]:
            text = re.sub(r"@\w+", "", text)

        if settings["replace_link"]:
            text = re.sub(r"https?://\S+", settings["replace_link"], text)

        elif settings["remove_links"]:
            text = re.sub(r"https?://\S+", "", text)

        for target in targets:

            try:

                reply = None

                if event.message.is_reply:
                    rid = event.message.reply_to_msg_id
                    reply = msg_map.get(rid, {}).get(target)

                if event.message.media:

                    sent = await client.send_file(
                        int(target),
                        event.message.media,
                        caption=text,
                        reply_to=reply
                    )

                else:

                    sent = await client.send_message(
                        int(target),
                        text,
                        reply_to=reply,
                        link_preview=False
                    )

                msg_map.setdefault(event.message.id, {})[target] = sent.id

            except Exception as e:
                print("Forward error:", e)


    # ALBUM FORWARD

    @client.on(events.Album)

    async def album_forward(event):

        data = load()

        sources = data["sources"]
        targets = data["targets"]

        cid = str(event.chat_id)

        if cid not in sources:
            return

        media = [msg.media for msg in event.messages]

        caption = event.messages[0].text or ""

        for target in targets:

            try:

                await client.send_file(
                    int(target),
                    media,
                    caption=caption
                )

            except Exception as e:
                print("Album error:", e)


    # DELETE SYNC

    @client.on(events.MessageDeleted)

    async def delete_sync(event):

        data = load()
        targets = data["targets"]

        for msg_id in event.deleted_ids:

            if msg_id in msg_map:

                for target, target_msg in msg_map[msg_id].items():

                    try:
                        await client.delete_messages(int(target), target_msg)
                    except:
                        pass


    # EDIT SYNC

    @client.on(events.MessageEdited)

    async def edit_sync(event):

        msg_id = event.message.id

        if msg_id not in msg_map:
            return

        for target, target_msg in msg_map[msg_id].items():

            try:

                await client.edit_message(
                    int(target),
                    target_msg,
                    event.message.text
                )

            except:
                pass


    await client.run_until_disconnected()
