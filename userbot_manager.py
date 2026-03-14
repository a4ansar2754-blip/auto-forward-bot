import os
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

# session folder
os.makedirs("sessions", exist_ok=True)

clients = {}
phone_code_hash = {}

async def login_user(user_id, phone=None, code=None):

    session_file = f"sessions/{user_id}"

    if user_id not in clients:
        client = TelegramClient(session_file, API_ID, API_HASH)
        await client.connect()
        clients[user_id] = client

    client = clients[user_id]

    # STEP 1 SEND OTP
    if phone:

        result = await client.send_code_request(phone)

        phone_code_hash[user_id] = result.phone_code_hash
        clients[user_id].phone = phone

        return "CODE"

    # STEP 2 VERIFY OTP
    if code:

        try:

            await client.sign_in(
                phone=client.phone,
                code=code,
                phone_code_hash=phone_code_hash[user_id]
            )

            return "SUCCESS"

        except Exception as e:

            print(e)
            return "FAIL"

    return "FAIL"
