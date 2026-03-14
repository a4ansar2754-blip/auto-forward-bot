import os
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

clients = {}
phone_hash = {}

os.makedirs("sessions", exist_ok=True)


async def login_user(user_id, phone=None, code=None):

    session_file = f"sessions/{user_id}"

    client = TelegramClient(session_file, API_ID, API_HASH)

    await client.connect()

    # STEP 1 → SEND OTP
    if phone:

        r = await client.send_code_request(phone)

        phone_hash[user_id] = r.phone_code_hash
        clients[user_id] = client

        return "CODE"

    # STEP 2 → VERIFY OTP
    if code:

        client = clients.get(user_id)

        await client.sign_in(
            code=code,
            phone_code_hash=phone_hash[user_id]
        )

        return "SUCCESS"
