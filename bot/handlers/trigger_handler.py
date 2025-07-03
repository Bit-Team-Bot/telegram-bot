# handlers/trigger_handler.py

import logging
from pyrogram.types import ChatPermissions

class TriggerHandler:
    def __init__(self, db):
        self.db = db
        self.logger = logging.getLogger(__name__)

    async def is_trigger(self, text, message=None):
        # Triggerworte und zugehörige Methoden
        triggers = {
            "news": self.send_news,
            "krypto-news": self.send_news,
            "crypto-news": self.send_news,
            "witz": self.send_joke,
            "joke": self.send_joke,
            "unmute": self.unmute_user,
            # weitere Triggerworte und Methoden hier ergänzen
        }
        key = text.strip().lower()
        self.logger.info(f"[TriggerHandler] Nachricht empfangen: '{key}'")
        if key in triggers and message is not None:
            self.logger.info(f"[TriggerHandler] Trigger erkannt: '{key}' -> {triggers[key].__name__}")
            await triggers[key](message)
            return True
        self.logger.info(f"[TriggerHandler] Kein Trigger für: '{key}'")
        return False

    async def send_news(self, message):
        await message.reply("📰 Hier sind die aktuellen Krypto-News! (Platzhalter)")

    async def send_joke(self, message):
        await message.reply("😂 Hier kommt ein Witz: Warum können Elefanten nicht fliegen? Weil sie zu schwer für den Flugzeugmodus sind.")

    async def unmute_user(self, message):
        try:
            await message.chat.restrict_member(
                message.from_user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
            await message.reply("🔊 Du wurdest entmutet und kannst wieder schreiben.")
        except Exception as e:
            await message.reply(f"❌ Fehler beim Entmuten: {e}")
