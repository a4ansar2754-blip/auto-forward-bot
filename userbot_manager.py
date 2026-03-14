from telethon import TelegramClient
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}
phone_hash = {}


async def login_user(user_id, phone=None, code=None):

    session_file = f"sessions/{user_id}"

    client = TelegramClient(session_file, API_ID, API_HASH)

    await client.connect()

    # STEP 1 SEND OTP
    if phone:

        r = await client.send_code_request(phone)

        phone_hash[user_id] = r.phone_code_hash

        clients[user_id] = client

        return "CODE"

    # STEP 2 VERIFY OTP
    if code:

        client = clients[user_id]

        await client.sign_in(
            code=code,
            phone_code_hash=phone_hash[user_id]
        )

        return "SUCCESS"
