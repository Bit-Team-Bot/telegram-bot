from telethon import TelegramClient, functions, types
from config import API_ID, API_HASH, SESSION_NAME   # Absoluter Import
import asyncio
from datetime import datetime, timedelta
import logging
import re

class UserbotHandler:
    def __init__(self):
        self.client = None
        self.is_running = False
        self.logger = logging.getLogger(__name__)
        self.pending_verifications = {}  # {phone: {"started_at": datetime, "message_handler": handler}}

    async def start(self):
        if self.is_running:
            return {"status": "already_running"}
        
        try:
            self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
            await self.client.start()
            self.is_running = True
            self.logger.info("Userbot erfolgreich gestartet")
            return {"status": "started"}
        except Exception as e:
            self.logger.error(f"Fehler beim Starten des Userbots: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def stop(self):
        if not self.is_running:
            return {"status": "not_running"}
        
        try:
            # Cleanup pending verifications
            for phone in list(self.pending_verifications.keys()):
                await self.cleanup_verification(phone)
            
            await self.client.disconnect()
            self.is_running = False
            self.logger.info("Userbot gestoppt")
            return {"status": "stopped"}
        except Exception as e:
            self.logger.error(f"Fehler beim Stoppen des Userbots: {str(e)}")
            return {"status": "error", "message": str(e)}

    async def get_status(self):
        return {
            "is_running": self.is_running,
            "session_name": SESSION_NAME,
            "pending_verifications": len(self.pending_verifications)
        }

    async def cleanup_verification(self, phone):
        """Cleanup für eine abgelaufene oder abgeschlossene Verifizierung"""
        if phone in self.pending_verifications:
            verification_data = self.pending_verifications[phone]
            if "message_handler" in verification_data:
                try:
                    self.client.remove_event_handler(verification_data["message_handler"])
                except:
                    pass
            del self.pending_verifications[phone]

    async def send_verification_code(self, phone):
        """Startet den echten Telegram-Verifizierungsprozess"""
        if not self.is_running:
            await self.start()
        
        # Cleanup alte Verifizierungen
        current_time = datetime.now()
        expired_phones = []
        for phone_key, data in self.pending_verifications.items():
            if current_time - data["started_at"] > timedelta(minutes=10):
                expired_phones.append(phone_key)
        
        for expired_phone in expired_phones:
            await self.cleanup_verification(expired_phone)
        
        # Prüfe ob bereits eine Verifizierung für diese Nummer läuft
        if phone in self.pending_verifications:
            return {"status": "error", "message": "Verifizierung bereits gestartet"}
        
        try:
            # Starte echte Telegram-Verifizierung
            result = await self.client.send_code_request(phone)
            
            # Speichere Verifizierungsdaten
            self.pending_verifications[phone] = {
                "started_at": datetime.now(),
                "phone_code_hash": result.phone_code_hash,
                "timeout": datetime.now() + timedelta(minutes=10)
            }
            
            self.logger.info(f"Verifizierungscode für {phone} angefordert")
            return {
                "status": "code_sent", 
                "phone": phone,
                "message": "Telegram-Code wurde an Ihre Nummer gesendet"
            }
            
        except Exception as e:
            self.logger.error(f"Fehler beim Senden des Verifizierungscodes: {str(e)}")
            return {"status": "error", "message": f"Fehler beim Senden des Codes: {str(e)}"}

    async def verify_code(self, phone, code):
        """Verifiziert den echten Telegram-Code"""
        if phone not in self.pending_verifications:
            return {"status": "error", "message": "Keine aktive Verifizierung für diese Nummer"}
        
        verification_data = self.pending_verifications[phone]
        
        # Prüfe Timeout
        if datetime.now() > verification_data["timeout"]:
            await self.cleanup_verification(phone)
            return {"status": "error", "message": "Verifizierung abgelaufen"}
        
        try:
            # Versuche mit dem Code zu signieren
            await self.client.sign_in(
                phone,
                code, 
                phone_code_hash=verification_data["phone_code_hash"]
            )
            
            # Erfolgreiche Verifizierung
            await self.cleanup_verification(phone)
            self.logger.info(f"Erfolgreiche Verifizierung für {phone}")
            
            return {"status": "success", "message": "Code erfolgreich verifiziert"}
            
        except Exception as e:
            self.logger.error(f"Verifizierungsfehler für {phone}: {str(e)}")
            
            # Bei zu vielen Versuchen: Cleanup
            if "too many attempts" in str(e).lower():
                await self.cleanup_verification(phone)
                return {"status": "error", "message": "Zu viele Versuche. Bitte starten Sie eine neue Verifizierung."}
            
            return {"status": "error", "message": "Ungültiger Code"}

    async def get_dialogs(self):
        if not self.is_running:
            await self.start()
        dialogs = []
        async for dialog in self.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                dialogs.append({
                    "id": dialog.id,
                    "title": dialog.title,
                    "type": "group" if dialog.is_group else "channel"
                })
        return dialogs

    async def create_group(self, title, supergroup=False):
        if not self.is_running:
            await self.start()
        try:
            if not supergroup:
                result = await self.client(functions.messages.CreateChatRequest(
                    users=[],
                    title=title
                ))
                chat = result.chats[0]
            else:
                result = await self.client(functions.channels.CreateChannelRequest(
                    title=title,
                    about="Automatisch erstellt",
                    megagroup=True
                ))
                chat = result.chats[0]
            return {
                "id": chat.id,
                "title": chat.title,
                "is_supergroup": getattr(chat, "megagroup", False)
            }
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Gruppe: {str(e)}")
            return {"error": str(e)}

    async def add_user_to_group(self, user_id, group_id):
        try:
            await self.client(functions.messages.AddChatUserRequest(
                chat_id=group_id,
                user_id=user_id,
                fwd_limit=10
            ))
            return {"status": "ok"}
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen des Users: {str(e)}")
            return {"error": str(e)}

    async def send_message(self, group_id, message):
        if not self.is_running:
            await self.start()
        try:
            await self.client.send_message(group_id, message)
            return {"status": "ok"}
        except Exception as e:
            self.logger.error(f"Fehler beim Senden der Nachricht: {str(e)}")
            return {"error": str(e)}

    async def transfer_ownership(self, group_id, new_owner_id):
        self.logger.info("Ownership-Transfer kann nur manuell erfolgen (Telegram-Vorgabe).")
        return {"status": "manual_required"}
