import sys
from telethon import TelegramClient
from config import API_ID, API_HASH

if len(sys.argv) < 2:
    print("Nummer fehlt!")
    sys.exit(1)

phone = sys.argv[1]
session_name = f"userbot_{phone}"
client = TelegramClient(session_name, API_ID, API_HASH)

async def main():
    await client.start(phone=phone)
    print(f"Userbot für {phone} gestartet!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
