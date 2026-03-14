import os
import asyncio
import re
from telethon import TelegramClient,events
from config_manager import get_config

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}

async def start_userbot(user_id):

    session = f"sessions/{user_id}.session"

    client = TelegramClient(session,API_ID,API_HASH)

    await client.start()

    clients[user_id] = client

    print("Userbot running:",user_id)

    @client.on(events.NewMessage)
    async def forward(e):

        data = get_config(user_id)

        sources = data["sources"]
        targets = data["targets"]
        s = data["settings"]

        if not s["forward"]:
            return

        cid = str(e.chat_id)

        if cid not in sources:
            return

        text = e.message.text or ""

        for w in s["blacklist"]:
            if w.lower() in text.lower():
                return

        if s["remove_username"]:
            text = re.sub(r"@\w+","",text)

        if s["replace_link"]:
            text = re.sub(r"https?://\S+",s["replace_link"],text)

        elif s["remove_links"]:
            text = re.sub(r"https?://\S+","",text)

        for t in targets:

            try:

                if e.media and s["media"]:

                    await client.send_file(
                        int(t),
                        e.media,
                        caption=text
                    )

                else:

                    await client.send_message(
                        int(t),
                        text,
                        link_preview=False
                    )

            except Exception as er:
                print(er)

    await client.run_until_disconnected()
