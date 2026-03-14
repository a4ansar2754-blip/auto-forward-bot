import os
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SESSION_DIR = "sessions"

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

clients = {}
login_data = {}

async def login_user(user, phone=None, code=None):

    session = f"{SESSION_DIR}/{user}"

    client = TelegramClient(session, API_ID, API_HASH)

    await client.connect()

    # STEP 1 SEND CODE
    if code is None:

        result = await client.send_code_request(phone)

        login_data[user] = {
            "phone": phone,
            "phone_code_hash": result.phone_code_hash,
            "client": client
        }

        return "CODE"

    # STEP 2 VERIFY OTP
    data = login_data.get(user)

    if not data:
        return "ERROR"

    client = data["client"]

    await client.sign_in(
        phone=data["phone"],
        code=code,
        phone_code_hash=data["phone_code_hash"]
    )

    clients[user] = client

    login_data.pop(user)

    return "SUCCESS"
