import os
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}

os.makedirs("sessions",exist_ok=True)

async def login_user(user,phone,code=None):

    session=f"sessions/{user}"

    client=TelegramClient(session,API_ID,API_HASH)

    await client.connect()

    if not await client.is_user_authorized():

        if code is None:

            await client.send_code_request(phone)
            return "CODE"

        else:

            await client.sign_in(phone,code)

    clients[user]=client

    return "SUCCESS"
