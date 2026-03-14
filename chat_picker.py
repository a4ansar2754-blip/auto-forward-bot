from telethon.tl.types import Channel
from userbot_manager import clients

chat_cache = {}


async def get_user_chats(user):

    client = clients.get(user)

    if not client:
        return []

    chats = []

    async for dialog in client.iter_dialogs():

        if isinstance(dialog.entity, Channel):
            chats.append(dialog)

        if len(chats) == 15:
            break

    chat_cache[user] = chats

    return chats


def get_chat(user, index):

    chats = chat_cache.get(user, [])

    if index < len(chats):
        return chats[index].entity.id

    return None
