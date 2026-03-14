import os
import re
import asyncio

from telethon import TelegramClient, events
from config_manager import get_config

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}
msg_map = {}
album_cache = {}


# ---------------- TEXT PROCESS ---------------- #

def process_text(text, settings):

    if not text:
        return ""

    # blacklist filter
    for w in settings.get("blacklist", []):
        if w.lower() in text.lower():
            return None

    # remove username
    if settings.get("remove_username"):
        text = re.sub(r"@\w+", "", text)

    # replace words
    replace_words = settings.get("replace_words", {})

    for old, new in replace_words.items():
        text = text.replace(old, new)

    # replace links
    if settings.get("replace_link"):
        text = re.sub(r"https?://\S+", settings["replace_link"], text)

    # remove links
    elif settings.get("remove_links"):
        text = re.sub(r"https?://\S+", "", text)

    # header
    if settings.get("header"):
        text = settings["header"] + "\n\n" + text

    # footer
    if settings.get("footer"):
        text = text + "\n\n" + settings["footer"]

    return text


# ---------------- AUTO DELETE ---------------- #

async def auto_delete(client, chat_id, msg_id, delay):

    if delay <= 0:
        return

    await asyncio.sleep(delay)

    try:
        await client.delete_messages(chat_id, msg_id)
    except:
        pass


# ---------------- START USERBOT ---------------- #

async def start_userbot(user_id):

    session = f"sessions/{user_id}"

    client = TelegramClient(session, API_ID, API_HASH)

    await client.start()

    clients[user_id] = client

    print("USERBOT STARTED:", user_id)


# ---------------- NEW MESSAGE ---------------- #

    @client.on(events.NewMessage)
    async def forward_handler(e):

        data = get_config(user_id)

        sources = data["sources"]
        targets = data["targets"]
        s = data["settings"]

        if not s.get("forward"):
            return

        cid = str(e.chat_id)

        if cid not in sources:
            return

        text = process_text(e.message.text or "", s)

        if text is None:
            return

        for t in targets:

            try:

                reply_id = None

                # reply chain sync
                if e.is_reply:

                    r = await e.get_reply_message()

                    if r and r.id in msg_map:

                        reply_id = msg_map[r.id].get(t)

                # album forward
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

                # media forward
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

                msg_map.setdefault(e.id, {})[t] = sent.id

                # auto delete
                if s.get("auto_delete"):

                    delay = s.get("delete_timer", 0)

                    asyncio.create_task(
                        auto_delete(client, int(t), sent.id, delay)
                    )

            except Exception as er:
                print(er)


# ---------------- EDIT SYNC ---------------- #

    @client.on(events.MessageEdited)
    async def edit_handler(e):

        data = get_config(user_id)

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


# ---------------- DELETE SYNC ---------------- #

    @client.on(events.MessageDeleted)
    async def delete_handler(e):

        data = get_config(user_id)

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


    await client.run_until_disconnected()
