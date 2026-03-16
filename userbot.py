import os
import json
import re
import asyncio

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

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


# =========================
# TEXT PROCESS
# =========================

def process_text(text, s):

    if not text:
        text = ""

    # blacklist
    for w in s.get("blacklist", []):
        if w.lower() in text.lower():
            return None

    # remove username
    if s.get("remove_username"):
        text = re.sub(r"@\w+", "", text)

    # replace links
    if s.get("replace_link"):
        text = re.sub(r"https?://\S+", s["replace_link"], text)

    # remove links
    elif s.get("remove_links"):
        text = re.sub(r"https?://\S+", "", text)

    return text.strip()


# =========================
# SAFE SEND SYSTEM
# =========================

async def safe_send(target, text=None, file=None, reply=None):

    if not text and not file:
        return None

    while True:

        try:

            if file:
                sent = await client.send_file(
                    int(target),
                    file,
                    caption=text if text else None,
                    reply_to=reply
                )
            else:
                sent = await client.send_message(
                    int(target),
                    text,
                    reply_to=reply,
                    link_preview=False
                )

            return sent

        except FloodWaitError as e:

            print("FloodWait:", e.seconds)
            await asyncio.sleep(e.seconds)

        except Exception as er:

            print("SEND ERROR:", er)
            return None


# =========================
# NEW MESSAGE HANDLER
# =========================

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

    text = process_text(e.text, s)

    if text is None:
        return

    for t in targets:

        try:

            reply_id = None

            if e.is_reply:

                r = await e.get_reply_message()

                if r and r.id in msg_map:
                    reply_id = msg_map[r.id].get(t)

            # ===== ALBUM SYSTEM =====

            if e.grouped_id:

                album_cache.setdefault(e.grouped_id, []).append(e)

                await asyncio.sleep(1)

                msgs = album_cache.pop(e.grouped_id, [])

                files = []

                for m in msgs:

                    if m.media:
                        file = await m.download_media()
                        files.append(file)

                sent = await safe_send(
                    t,
                    text,
                    files,
                    reply_id
                )

            # ===== MEDIA =====

            elif e.media and s.get("media"):

                file = await e.download_media()

                sent = await safe_send(
                    t,
                    text,
                    file,
                    reply_id
                )

            # ===== TEXT =====

            else:

                sent = await safe_send(
                    t,
                    text,
                    None,
                    reply_id
                )

            if not sent:
                continue

            # ===== FIX LIST BUG =====

            if isinstance(sent, list):

                msg_map.setdefault(e.id, {})[t] = sent[0].id

            else:

                msg_map.setdefault(e.id, {})[t] = sent.id

        except Exception as er:

            print("FORWARD ERROR:", er)


# =========================
# EDIT SYNC
# =========================

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
                await client.edit_message(int(t), mid, text)

        except:
            pass


# =========================
# DELETE SYNC
# =========================

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
                    await client.delete_messages(int(t), tid)

            except:
                pass


# =========================
# START USERBOT
# =========================

async def start_userbot():

    await client.start()

    print("USERBOT RUNNING")

    await client.run_until_disconnected()
