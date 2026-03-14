import os
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}

SESSION_DIR = "sessions"

async def login_user(user, phone, code=None):

    if not os.path.isdir(SESSION_DIR):
        os.mkdir(SESSION_DIR)

    session_file = f"{SESSION_DIR}/{user}"

    client = TelegramClient(session_file, API_ID, API_HASH)

    await client.connect()

    if not await client.is_user_authorized():

        if code is None:
            await client.send_code_request(phone)
            return "CODE"

        else:
            await client.sign_in(phone, code)

    clients[user] = client

    return "SUCCESS"
