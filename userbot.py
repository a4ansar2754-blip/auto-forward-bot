import os
import json
import re
import asyncio

from telethon import TelegramClient, events

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

CONFIG_FILE = "config.json"

msg_map = {}
album_cache = {}

def load():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def process_text(text, s):

    if not text:
        return ""

    for w in s.get("blacklist", []):
        if w.lower() in text.lower():
            return None

    if s.get("remove_username"):
        text = re.sub(r"@\w+", "", text)

    replace_words = s.get("replace_words", {})

    for old,new in replace_words.items():
        text = text.replace(old,new)

    if s.get("replace_link"):
        text = re.sub(r"https?://\S+",s["replace_link"],text)

    elif s.get("remove_links"):
        text = re.sub(r"https?://\S+","",text)

    if s.get("header"):
        text = s["header"] + "\n\n" + text

    if s.get("footer"):
        text = text + "\n\n" + s["footer"]

    return text


async def start_userbot(user_id):

    session = f"sessions/{user_id}.session"

    client = TelegramClient(session,API_ID,API_HASH)

    await client.start()

    print("USERBOT STARTED",user_id)


    @client.on(events.NewMessage)
    async def forward_handler(e):

        data = load()

        sources = data["sources"]
        targets = data["targets"]
        s = data["settings"]

        if not s.get("forward"):
            return

        cid = str(e.chat_id)

        if cid not in sources:
            return

        text = process_text(e.message.text or "",s)

        if text is None:
            return

        for t in targets:

            try:

                reply_id = None

                if e.is_reply:

                    r = await e.get_reply_message()

                    if r and r.id in msg_map:

                        reply_id = msg_map[r.id].get(t)

                if e.grouped_id:

                    album_cache.setdefault(e.grouped_id,[]).append(e)

                    await asyncio.sleep(1)

                    msgs = album_cache.pop(e.grouped_id,[])

                    files = [m.media for m in msgs]

                    sent = await client.send_file(
                        int(t),
                        files,
                        caption=text,
                        reply_to=reply_id
                    )

                elif e.media and s.get("media"):

                    sent = await client.send_file(
                        int(t),
                        e.media,
                        caption=text,
                        reply_to=reply_id
                    )

                else:

                    sent = await client.send_message(
                        int(t),
                        text,
                        reply_to=reply_id,
                        link_preview=False
                    )

                msg_map.setdefault(e.id,{})[t] = sent.id

            except Exception as er:
                print(er)

    await client.run_until_disconnected()
