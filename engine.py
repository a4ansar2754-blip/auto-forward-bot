import asyncio
from telethon import events
from userbot_manager import clients
from config_manager import get_config

album_cache = {}

def start_engine(user):

    client = clients[user]

    @client.on(events.NewMessage)
    async def forward(event):

        data = get_config(user)

        if str(event.chat_id) not in data["sources"]:
            return

        text = event.raw_text or ""

        # block links
        if "http" in text:
            return

        reply_map = {}

        for target in data["targets"]:

            if event.grouped_id:

                album_cache.setdefault(event.grouped_id,[]).append(event)

                await asyncio.sleep(1)

                msgs = album_cache.pop(event.grouped_id,[])

                files = [m.media for m in msgs]

                await client.send_file(
                    int(target),
                    files,
                    caption=text
                )

            elif event.media:

                sent = await client.send_file(
                    int(target),
                    event.media,
                    caption=text
                )

                reply_map[event.id] = sent.id

            else:

                sent = await client.send_message(
                    int(target),
                    text
                )

                reply_map[event.id] = sent.id

            # auto delete
            asyncio.create_task(auto_delete(client,target,sent.id))

async def auto_delete(client,chat,msg):

    await asyncio.sleep(60)

    try:
        await client.delete_messages(int(chat),msg)
    except:
        pass
