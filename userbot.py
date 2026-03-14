from telethon import TelegramClient
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

client = TelegramClient("session", API_ID, API_HASH)

async def start_userbot():

    await client.start()

    print("USERBOT STARTED")

    await client.run_until_disconnected()
