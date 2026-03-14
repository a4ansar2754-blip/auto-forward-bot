from telethon import events
from userbot_manager import clients
from config_manager import get_config

def start_engine(user_id):

    client = clients[user_id]

    @client.on(events.NewMessage)
    async def forward(event):

        data = get_config(user_id)

        if str(event.chat_id) not in data["sources"]:
            return

        for target in data["targets"]:

            if event.media:

                await client.send_file(
                    int(target),
                    event.media,
                    caption=event.text
                )

            else:

                await client.send_message(
                    int(target),
                    event.text
                )
