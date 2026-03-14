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


def clean_text(text, settings):

    if not text:
        return ""

    for w in settings["blacklist"]:
        if w.lower() in text.lower():
            return None

    if settings["remove_username"]:
        text = re.sub(r"@\w+", "", text)

    if settings["replace_link"]:
        text = re.sub(r"https?://\S+", settings["replace_link"], text)

    elif settings["remove_links"]:
        text = re.sub(r"https?://\S+", "", text)

    return text


async def start_userbot():

    await client.start()
    print("USERBOT RUNNING")

    @client.on(events.NewMessage)
    async def forward(e):

        data = load()

        sources = data["sources"]
        targets = data["targets"]
        s = data["settings"]

        if not s["forward"]:
            return

        cid = str(e.chat_id)

        if cid not in sources:
            return

        text = clean_text(e.message.text or "", s)

        if text is None:
            return

        for t in targets:

            try:

                if e.media and s["media"]:

                    sent = await client.send_file(
                        int(t),
                        e.media,
                        caption=text
                    )

                else:

                    sent = await client.send_message(
                        int(t),
                        text,
                        link_preview=False
                    )

                msg_map.setdefault(e.id, {})[t] = sent.id

            except Exception as er:
                print(er)

    await client.run_until_disconnected()
