import os
import json
import re
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

CONFIG_FILE = "config.json"

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

msg_map = {}
album_cache = {}

def load():
    with open(CONFIG_FILE) as f:
        return json.load(f)


# TEXT MODIFIER
def modify_text(text, s):

    if not text:
        return ""

    # blacklist
    for w in s["blacklist"]:
        if w.lower() in text.lower():
            return None

    # username remove
    if s["remove_username"]:
        text = re.sub(r"@\w+", "", text)

    # link replace
    if s["replace_link"]:
        text = re.sub(r"https?://\S+", s["replace_link"], text)

    # remove links
    elif s["remove_links"]:
        text = re.sub(r"https?://\S+", "", text)

    # word replace
    if "replace_words" in s:
        for a,b in s["replace_words"].items():
            text = text.replace(a,b)

    # header
    if s.get("header"):
        text = s["header"] + "\n\n" + text

    # footer
    if s.get("footer"):
        text = text + "\n\n" + s["footer"]

    return text


async def start_userbot():

    await client.start()

    print("USERBOT STARTED")


# ===============================
# MESSAGE FORWARD
# ===============================

@client.on(events.NewMessage)
async def forward_handler(e):

    data = load()

    sources = data["sources"]
    targets = data["targets"]
    s = data["settings"]

    if not s["forward"]:
        return

    cid = str(e.chat_id)

    if cid not in sources:
        return

    text = modify_text(e.message.text or "", s)

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

                album_cache.setdefault(e.grouped_id, []).append(e)

                await asyncio.sleep(1)

                msgs = album_cache.pop(e.grouped_id, [])

                files = [m.media for m in msgs]

                sent = await client.send_file(
                    int(t),
                    files,
                    caption=text,
                    reply_to=reply_id
                )

            elif e.media and s["media"]:

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

            # auto delete
            if s["auto_delete"]:
                asyncio.create_task(delete_later(t,sent.id))

        except Exception as er:
            print(er)


# ===============================
# DELETE TIMER
# ===============================

async def delete_later(chat,msg):

    data = load()

    delay = data["settings"].get("delete_timer",0)

    if delay <= 0:
        return

    await asyncio.sleep(delay)

    try:
        await client.delete_messages(int(chat),msg)
    except:
        pass


# ===============================
# EDIT SYNC
# ===============================

@client.on(events.MessageEdited)
async def edit_handler(e):

    data = load()

    targets = data["targets"]

    if e.id not in msg_map:
        return

    text = e.text or ""

    for t in targets:

        try:

            mid = msg_map[e.id].get(t)

            if mid:

                await client.edit_message(
                    int(t),
                    mid,
                    text
                )

        except:
            pass


# ===============================
# DELETE SYNC
# ===============================

@client.on(events.MessageDeleted)
async def delete_handler(e):

    data = load()

    targets = data["targets"]

    for mid in e.deleted_ids:

        if mid not in msg_map:
            continue

        for t in targets:

            try:

                tid = msg_map[mid].get(t)

                if tid:
                    await client.delete_messages(int(t),tid)

            except:
                pass


async def run():
    await client.run_until_disconnected()
