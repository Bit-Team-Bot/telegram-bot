from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os

WEBUI_URL = os.getenv("WEBUI_URL", "https://webui.bit-team-bot.online")

@Client.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Webinterface öffnen", url=WEBUI_URL)]
    ])
    await message.reply(
        "Willkommen! Hier kannst du das Webinterface öffnen:",
        reply_markup=keyboard
    )

@Client.on_message(filters.command("start") & (filters.group | filters.channel))
async def start_group(client: Client, message: Message):
    await message.reply(
        "ℹ️ Das Webinterface ist nur im Privat-Chat verfügbar. Bitte schreibe mir privat /start."
    ) 