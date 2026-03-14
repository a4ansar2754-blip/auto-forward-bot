import asyncio
import re
from telethon import events

from userbot_manager import clients
from config_manager import get_config

running = {}
reply_map = {}
album_cache = {}

async def start_engine(user):

    if user not in clients:
        return

    client = clients[user]

    if user in running:
        return

    running[user] = True

    config = get_config(user)

    sources = config["sources"]
    targets = config["targets"]

    @client.on(events.NewMessage(chats=sources))
    async def forward_handler(event):

        msg = event.message
        text = msg.text or ""

        config = get_config(user)

        for k in config["keywords"]:
            if k.lower() in text.lower():
                return

        if config["replace_link"]:
            text = re.sub(r"http\S+", config["replace_link"], text)

        if config["header"]:
            text = config["header"] + "\n\n" + text

        if config["footer"]:
            text = text + "\n\n" + config["footer"]

        if config["delay"]:
            await asyncio.sleep(config["delay"])

        for target in targets:

            reply_id = None

            if msg.reply_to_msg_id in reply_map:
                reply_id = reply_map[msg.reply_to_msg_id]

            if msg.grouped_id:

                album_cache.setdefault(msg.grouped_id, []).append(msg)

                await asyncio.sleep(1)

                msgs = album_cache.pop(msg.grouped_id, [])

                files = [m.media for m in msgs]

                sent = await client.send_file(
                    target,
                    files,
                    caption=text
                )

            elif msg.media:

                sent = await client.send_file(
                    target,
                    msg.media,
                    caption=text,
                    reply_to=reply_id
                )

            else:

                sent = await client.send_message(
                    target,
                    text,
                    reply_to=reply_id
                )

            reply_map[msg.id] = sent.id

            if config["autodelete"]:

                await asyncio.sleep(config["autodelete"])

                await client.delete_messages(target, sent.id)


async def stop_engine(user):

    if user in running:
        running.pop(user)
