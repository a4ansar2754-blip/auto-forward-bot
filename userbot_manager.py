import os
from telethon import TelegramClient
from telethon.sessions import StringSession

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}

async def login_user(user_id, phone, code=None, password=None):

    session_file = f"sessions/{user_id}.session"

    client = TelegramClient(session_file, API_ID, API_HASH)

    await client.connect()

    if not await client.is_user_authorized():

        if code is None:
            await client.send_code_request(phone)
            return "CODE"

        try:
            await client.sign_in(phone=phone, code=code)

        except Exception as e:

            if "password" in str(e):

                if password:
                    await client.sign_in(password=password)
                else:
                    return "PASSWORD"

    clients[user_id] = client

    return "SUCCESS"
