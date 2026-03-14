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

    if not os.path.exists(CONFIG_FILE):
        return {"sources": {}, "targets": {}, "settings": {}}

    with open(CONFIG_FILE) as f:
        return json.load(f)


async def start_userbot():

    await client.start()

    print("USERBOT RUNNING")

    @client.on(events.NewMessage)

    async def forward_handler(event):

        data = load()

        sources = data.get("sources", {})
        targets = data.get("targets", {})
        settings = data.get("settings", {})

        # forward disabled
        if not settings.get("forward", True):
            return

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        text = event.message.text or ""

        # blacklist filter
        for word in settings.get("blacklist", []):
            if word.lower() in text.lower():
                return

        # remove usernames
        if settings.get("remove_username"):
            text = re.sub(r"@\w+", "", text)

        # replace links
        if settings.get("replace_link"):
            text = re.sub(r"https?://\S+", settings["replace_link"], text)

        # remove links
        elif settings.get("remove_links"):
            text = re.sub(r"https?://\S+", "", text)

        for target_id in targets:

            try:

                reply_to = None

                if event.message.is_reply:
                    reply_id = event.message.reply_to_msg_id
                    reply_to = msg_map.get(reply_id, {}).get(target_id)

                if event.message.media:

                    sent = await client.send_file(
                        int(target_id),
                        event.message.media,
                        caption=text,
                        reply_to=reply_to
                    )

                else:

                    sent = await client.send_message(
                        int(target_id),
                        text,
                        reply_to=reply_to,
                        link_preview=False
                    )

                msg_map.setdefault(event.message.id, {})[target_id] = sent.id

            except Exception as e:
                print("Forward error:", e)

    await client.run_until_disconnected()
