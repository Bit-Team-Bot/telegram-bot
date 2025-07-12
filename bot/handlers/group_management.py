from pyrogram.types import Message, ChatPermissions
from pyrogram.client import Client
from typing import Optional
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class GroupManagement:
    def __init__(self, client: Client):
        self.client = client
        self.night_mode_status = {}  # Cache für Nachtmodus pro Chat
        self.group_settings = {}  # Cache für Gruppeneinstellungen pro Chat

    def get_default_welcome_message(self) -> str:
        return (
            "👋 Hallo zusammen! Ich bin der Bit-Team-Bot.\n\n"
            "Ich unterstütze euch mit automatischer Gruppenverwaltung und vielen nützlichen Features:\n\n"
            "**Gruppenverwaltung – Was ich für Admins kann:**\n"
            "• User automatisch begrüßen (mit persönlicher Ansprache)\n"
            "• Willkommensnachrichten frei definierbar (inkl. Platzhalter für Usernamen)\n"
            "• User muten, verwarnen, kicken (per Knopfdruck oder automatisch)\n"
            "• Gruppen nachts automatisch schließen/öffnen (\"Nachtmodus\" mit Info-Text)\n"
            "• Automatische Nachrichten zu bestimmten Zeiten senden (z. B. tägliche Infos)\n"
            "• Nachrichtenweiterleitung & Screenshots unterbinden\n"
            "• Regeln & Begrüßungstexte jederzeit anpassbar\n"
            "• Aktive User-Überwachung (optional)\n"
            "• Integration mit Webinterface für volle Kontrolle\n\n"
            "**Weitere Funktionen:**\n"
            "– Automatisierte Nachrichten- und Signalweiterleitung (Premium)\n"
            "– API- und Integrationen (Pro/Expert)\n"
            "– Statistiken und Reports\n"
            "– Multi-Language Support\n\n"
            "**So geht's los:**\n"
            "1. Schreibe <b>/start</b> im <b>privaten Chat</b> mit mir, um das Webinterface zu öffnen.\n"
            "2. Als Admin kannst du in der Gruppe das Menü mit <b>/menu</b> aufrufen.\n"
            "3. Alle Einstellungen für diese Gruppe kannst du im Webinterface verwalten.\n"
            "4. Hilfe jederzeit mit /help.\n\n"
            "Bei Fragen einfach /help in die Gruppe schreiben!"
        )

    async def get_group_settings(self, chat_id: int) -> dict:
        if chat_id not in self.group_settings:
            self.group_settings[chat_id] = {
                "welcome_message": self.get_default_welcome_message(),
                # Hier können weitere Einstellungen ergänzt werden
            }
        return self.group_settings[chat_id]

    async def update_group_settings(self, chat_id: int, settings: dict):
        current = await self.get_group_settings(chat_id)
        current.update(settings)
        self.group_settings[chat_id] = current

    async def on_bot_added_to_group(self, message: Message):
        chat_id = message.chat.id
        settings = await self.get_group_settings(chat_id)
        welcome_text = settings.get("welcome_message", self.get_default_welcome_message())
        # --- Backend-Registrierung der Gruppe ---
        try:
            from bot.bot import backend_client
            # Versuche, den User zu ermitteln, der den Bot hinzugefügt hat
            owner_id = None
            if message.from_user:
                owner_id = message.from_user.id
            backend_client.post("/groups/", {
                "group_id": str(chat_id),
                "owner_id": owner_id or 0,
                "name": message.chat.title or None
            })
            logger.info(f"Gruppe {chat_id} wurde im Backend registriert.")
        except Exception as e:
            logger.error(f"Fehler bei der Backend-Registrierung der Gruppe {chat_id}: {e}")
        # Logging vor dem Senden
        logger.info(f"[DEBUG] Sende Begrüßungsnachricht an Gruppe {chat_id}: {welcome_text}")
        try:
            await message.reply(welcome_text)
            logger.info(f"[DEBUG] Begrüßungsnachricht erfolgreich an Gruppe {chat_id} gesendet.")
        except Exception as e:
            logger.error(f"[ERROR] Begrüßungsnachricht konnte nicht an Gruppe {chat_id} gesendet werden: {e}")
        logger.info(f"Bot wurde zu Gruppe {chat_id} hinzugefügt.")

    async def on_new_member(self, message: Message):
        logger = logging.getLogger(__name__)
        try:
            user = message.new_chat_members[0]
            chat_id = message.chat.id
            logger.info(f"[DEBUG] on_new_member: user_id={user.id}, chat_id={chat_id}, user={user}")
            settings = await self.get_group_settings(chat_id)
            welcome_text = settings.get("welcome_message", self.get_default_welcome_message())
            logger.info(f"[DEBUG] welcome_text (vor Platzhalter): {welcome_text}")
            # Platzhalter ersetzen
            try:
                welcome_text = welcome_text.replace("{username}", user.first_name or "User")
                welcome_text = welcome_text.replace("{mention}", getattr(user, "mention", str(user.id)))
                welcome_text = welcome_text.replace("{group_name}", message.chat.title)
            except Exception as e:
                logger.error(f"[DEBUG] Fehler beim Platzhalter-Ersatz: {e}")
            logger.info(f"[DEBUG] welcome_text (nach Platzhalter): {welcome_text}")
            await message.reply(welcome_text)
            logger.info(f"Neues Mitglied {user.id} in Gruppe {chat_id} begrüßt.")
        except Exception as e:
            logger.error(f"[DEBUG] Fehler in on_new_member: {e}")

    async def on_member_left(self, message: Message):
        user = message.left_chat_member
        chat_id = message.chat.id
        bye_text = f"👋 {user.mention} hat die Gruppe verlassen."
        await message.reply(bye_text)
        logger.info(f"Mitglied {user.id} hat Gruppe {chat_id} verlassen.")

    async def toggle_night_mode(self, chat_id: int, enabled: Optional[bool] = None):
        # Nachtmodus-Status toggeln oder setzen
        if enabled is None:
            enabled = not self.night_mode_status.get(chat_id, False)
        self.night_mode_status[chat_id] = enabled
        status = "aktiviert" if enabled else "deaktiviert"
        logger.info(f"Nachtmodus für Gruppe {chat_id} wurde {status}.")
        # Hier könntest du z.B. den Chat schließen/öffnen
        return enabled

    async def mute_user(self, chat_id: int, user_id: int, duration: int = 300, reason: str = ""):
        # User muten mit ChatPermissions und datetime
        until_date = datetime.utcnow() + timedelta(seconds=duration)
        try:
            await self.client.restrict_chat_member(
                chat_id,
                user_id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            logger.info(f"User {user_id} in Gruppe {chat_id} für {duration}s gemutet. Grund: {reason}")
        except Exception as e:
            logger.error(f"Fehler beim Muten von User {user_id} in {chat_id}: {e}")

    async def warn_user(self, chat_id: int, user_id: int, reason: str = ""):
        logger.info(f"User {user_id} in Gruppe {chat_id} verwarnt. Grund: {reason}")
        await self.client.send_message(chat_id, f"⚠️ User {user_id} wurde verwarnt. Grund: {reason}")

    async def kick_user(self, chat_id: int, user_id: int, reason: str = ""):
        # User kicken (ban_chat_member in Pyrogram)
        try:
            await self.client.ban_chat_member(chat_id, user_id)
            logger.info(f"User {user_id} aus Gruppe {chat_id} entfernt. Grund: {reason}")
        except Exception as e:
            logger.error(f"Fehler beim Kicken von User {user_id} in {chat_id}: {e}")

    async def send_scheduled_message(self, chat_id: int, message_text: str, schedule_time: str):
        await self.client.send_message(chat_id, f"[Geplant für {schedule_time}] {message_text}")
        logger.info(f"Geplante Nachricht an {chat_id}: {message_text} ({schedule_time})") 