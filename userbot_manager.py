import os
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}

# folder create safely
if not os.path.exists("sessions"):
    os.mkdir("sessions")

async def login_user(user, phone, code=None):

    session_file = f"sessions/{user}"

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
