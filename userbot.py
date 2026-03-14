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


def load_config():

    if not os.path.exists(CONFIG_FILE):
        return {
            "sources": {},
            "targets": {},
            "settings": {}
        }

    with open(CONFIG_FILE) as f:
        return json.load(f)


# ---------------- FILTER TEXT ----------------

def clean_text(text, settings):

    if not text:
        return ""

    # blacklist
    for w in settings.get("blacklist", []):
        if w.lower() in text.lower():
            return None

    # remove username
    if settings.get("remove_username"):
        text = re.sub(r"@\w+", "", text)

    # replace links
    if settings.get("replace_link"):
        text = re.sub(r"https?://\S+", settings["replace_link"], text)

    # remove links
    elif settings.get("remove_links"):
        text = re.sub(r"https?://\S+", "", text)

    return text.strip()


# ---------------- START USERBOT ----------------

async def start_userbot():

    await client.start()

    print("USERBOT STARTED")

    # ---------------- MESSAGE FORWARD ----------------

    @client.on(events.NewMessage)
    async def forward_handler(event):

        data = load_config()

        sources = data.get("sources", {})
        targets = data.get("targets", {})
        settings = data.get("settings", {})

        if not settings.get("forward", True):
            return

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        text = event.message.text or ""

        text = clean_text(text, settings)

        if text is None:
            return

        for target in targets.keys():

            try:

                reply_to = None

                if event.message.is_reply:

                    rid = event.message.reply_to_msg_id

                    reply_to = msg_map.get(rid, {}).get(target)

                if event.message.media:

                    if not settings.get("media", True):
                        continue

                    sent = await client.send_file(
                        int(target),
                        event.message.media,
                        caption=text,
                        reply_to=reply_to
                    )

                else:

                    sent = await client.send_message(
                        int(target),
                        text,
                        reply_to=reply_to,
                        link_preview=False
                    )

                msg_map.setdefault(event.message.id, {})[target] = sent.id

            except Exception as e:
                print("Forward error:", e)

    # ---------------- ALBUM FORWARD ----------------

    @client.on(events.Album)
    async def album_forward(event):

        data = load_config()

        sources = data.get("sources", {})
        targets = data.get("targets", {})
        settings = data.get("settings", {})

        if not settings.get("media", True):
            return

        chat_id = str(event.chat_id)

        if chat_id not in sources:
            return

        files = []
        caption = ""

        for msg in event.messages:

            if msg.media:
                files.append(msg.media)

            if msg.text and caption == "":
                caption = msg.text

        caption = clean_text(caption, settings)

        if caption is None:
            return

        for target in targets.keys():

            try:

                sent = await client.send_file(
                    int(target),
                    files,
                    caption=caption
                )

                for i, msg in enumerate(event.messages):
                    msg_map.setdefault(msg.id, {})[target] = sent[i].id

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

        data = load_config()
        settings = data.get("settings", {})

        text = event.message.text or ""

        text = clean_text(text, settings)

        if text is None:
            return

        for target_id, target_msg in msg_map[msg_id].items():

            try:

                await client.edit_message(
                    int(target_id),
                    target_msg,
                    text
                )

            except:
                pass

    await client.run_until_disconnected()
