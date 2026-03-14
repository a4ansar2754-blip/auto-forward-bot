import asyncio
import re
from telethon import events
from userbot_manager import clients
from config_manager import get_config

running_engines = {}


async def start_engine(user):

    if user not in clients:
        return

    client = clients[user]

    if user in running_engines:
        return

    running_engines[user] = True

    config = get_config(user)

    sources = config.get("sources", {})
    targets = config.get("targets", {})

    blacklist = config.get("blacklist", [])
    replace_links = config.get("replace_links", {})
    header = config.get("header", "")
    footer = config.get("footer", "")
    delay = config.get("delay", 0)
    auto_delete = config.get("auto_delete", 0)

    @client.on(events.NewMessage(chats=list(sources.values())))
    async def handler(event):

        msg = event.message

        text = msg.text or ""

        # KEYWORD BLOCK
        for word in blacklist:
            if word.lower() in text.lower():
                return

        # LINK REMOVE
        text = re.sub(r"http\S+", "", text)

        # LINK REPLACE
        for old, new in replace_links.items():
            text = text.replace(old, new)

        # HEADER FOOTER
        if header:
            text = f"{header}\n\n{text}"

        if footer:
            text = f"{text}\n\n{footer}"

        # DELAY
        if delay > 0:
            await asyncio.sleep(delay)

        for target in targets.values():

            try:

                sent = await client.send_message(
                    target,
                    text,
                    file=msg.media
                )

                # AUTO DELETE
                if auto_delete > 0:

                    await asyncio.sleep(auto_delete)

                    await sent.delete()

            except Exception:
                pass


async def stop_engine(user):

    if user in running_engines:
        running_engines.pop(user)
