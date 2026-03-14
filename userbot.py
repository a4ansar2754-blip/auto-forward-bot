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

    await client.run_until_disconnected()
