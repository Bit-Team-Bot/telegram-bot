"""
Userbot Manager - Telegram-Session-Handling pro Telefonnummer
"""

import asyncio
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import os
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneCodeInvalidError,
    SessionPasswordNeededError,
    PhoneNumberInvalidError
)

logger = logging.getLogger(__name__)

class UserbotManager:
    """Manager für Telegram Userbot-Sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, TelegramClient] = {}
        self.session_data: Dict[str, Dict] = {}
        self.api_id = int(os.getenv("API_ID", "22239623"))
        self.api_hash = os.getenv("API_HASH", "15bd9602ec63cf438ad5b3efffbce58a")
        self.session_dir = Path("sessions")
        self.session_dir.mkdir(exist_ok=True)
        
    async def create_session(self, phone_number: str) -> Dict:
        """Neue Telegram-Session erstellen"""
        try:
            session_name = f"userbot_{phone_number.replace('+', '').replace(' ', '')}"
            session_path = self.session_dir / f"{session_name}.session"
            
            # Client erstellen
            client = TelegramClient(str(session_path), self.api_id, self.api_hash)
            
            # Session-Daten speichern
            self.session_data[phone_number] = {
                "phone_number": phone_number,
                "session_name": session_name,
                "created_at": datetime.utcnow(),
                "status": "created",
                "client": client
            }
            
            logger.info(f"Session für {phone_number} erstellt")
            
            return {
                "success": True,
                "phone_number": phone_number,
                "session_name": session_name,
                "requires_code": True
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Session für {phone_number}: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_code(self, phone_number: str) -> Dict:
        """Login-Code an Telefonnummer senden"""
        try:
            if phone_number not in self.session_data:
                return {"success": False, "error": "Session nicht gefunden"}
            
            client = self.session_data[phone_number]["client"]
            
            # Code senden
            await client.connect()
            sent_code = await client.send_code_request(phone_number)
            
            # Session-Status aktualisieren
            self.session_data[phone_number]["status"] = "code_sent"
            self.session_data[phone_number]["phone_code_hash"] = sent_code.phone_code_hash
            
            logger.info(f"Code an {phone_number} gesendet")
            
            return {
                "success": True,
                "phone_number": phone_number,
                "phone_code_hash": sent_code.phone_code_hash,
                "type": str(sent_code.type)
            }
            
        except PhoneNumberInvalidError:
            return {"success": False, "error": "Ungültige Telefonnummer"}
        except Exception as e:
            logger.error(f"Fehler beim Senden des Codes an {phone_number}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def verify_code(self, phone_number: str, code: str, password: Optional[str] = None) -> Dict:
        """Login-Code verifizieren"""
        try:
            if phone_number not in self.session_data:
                return {"success": False, "error": "Session nicht gefunden"}
            
            client = self.session_data[phone_number]["client"]
            phone_code_hash = self.session_data[phone_number].get("phone_code_hash")
            
            if not phone_code_hash:
                return {"success": False, "error": "Kein Code gesendet"}
            
            # Code verifizieren
            try:
                await client.sign_in(phone_number, code, phone_code_hash=phone_code_hash)
            except SessionPasswordNeededError:
                if not password:
                    return {"success": False, "error": "2FA-Passwort erforderlich", "requires_2fa": True}
                await client.sign_in(password=password)
            
            # Session aktivieren
            self.active_sessions[phone_number] = client
            self.session_data[phone_number]["status"] = "active"
            self.session_data[phone_number]["activated_at"] = datetime.utcnow()
            
            # User-Informationen abrufen
            me = await client.get_me()
            
            logger.info(f"Session für {phone_number} erfolgreich aktiviert")
            
            return {
                "success": True,
                "phone_number": phone_number,
                "user_id": me.id,
                "username": me.username,
                "first_name": me.first_name,
                "last_name": me.last_name
            }
            
        except PhoneCodeInvalidError:
            return {"success": False, "error": "Ungültiger Code"}
        except SessionPasswordNeededError:
            return {"success": False, "error": "2FA-Passwort erforderlich", "requires_2fa": True}
        except Exception as e:
            logger.error(f"Fehler bei der Code-Verifikation für {phone_number}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_session_status(self, phone_number: str) -> Dict:
        """Session-Status abrufen"""
        if phone_number not in self.session_data:
            return {"success": False, "error": "Session nicht gefunden"}
        
        session_info = self.session_data[phone_number]
        is_active = phone_number in self.active_sessions
        
        return {
            "success": True,
            "phone_number": phone_number,
            "status": session_info["status"],
            "is_active": is_active,
            "created_at": session_info["created_at"],
            "activated_at": session_info.get("activated_at")
        }
    
    async def disconnect_session(self, phone_number: str) -> Dict:
        """Session trennen"""
        try:
            if phone_number in self.active_sessions:
                client = self.active_sessions[phone_number]
                await client.disconnect()
                del self.active_sessions[phone_number]
                
                # Status aktualisieren
                if phone_number in self.session_data:
                    self.session_data[phone_number]["status"] = "disconnected"
                
                logger.info(f"Session für {phone_number} getrennt")
                
                return {"success": True, "message": "Session getrennt"}
            else:
                return {"success": False, "error": "Keine aktive Session gefunden"}
                
        except Exception as e:
            logger.error(f"Fehler beim Trennen der Session für {phone_number}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def send_message(self, phone_number: str, chat_id: int, message: str) -> Dict:
        """Nachricht über Userbot senden"""
        try:
            if phone_number not in self.active_sessions:
                return {"success": False, "error": "Keine aktive Session"}
            
            client = self.active_sessions[phone_number]
            
            # Nachricht senden
            sent_message = await client.send_message(chat_id, message)
            
            return {
                "success": True,
                "message_id": sent_message.id,
                "chat_id": chat_id
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Senden der Nachricht: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_chats(self, phone_number: str) -> Dict:
        """Verfügbare Chats abrufen"""
        try:
            if phone_number not in self.active_sessions:
                return {"success": False, "error": "Keine aktive Session"}
            
            client = self.active_sessions[phone_number]
            
            # Chats abrufen
            chats = []
            async for dialog in client.iter_dialogs():
                chats.append({
                    "id": dialog.id,
                    "name": dialog.name,
                    "type": str(dialog.entity.__class__.__name__),
                    "unread_count": dialog.unread_count
                })
            
            return {
                "success": True,
                "chats": chats
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Chats: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_inactive_sessions(self):
        """Inaktive Sessions bereinigen"""
        current_time = datetime.utcnow()
        inactive_threshold = timedelta(hours=24)
        
        sessions_to_remove = []
        
        for phone_number, session_info in self.session_data.items():
            if session_info["status"] == "created":
                created_at = session_info["created_at"]
                if current_time - created_at > inactive_threshold:
                    sessions_to_remove.append(phone_number)
        
        for phone_number in sessions_to_remove:
            await self.disconnect_session(phone_number)
            del self.session_data[phone_number]
            logger.info(f"Inaktive Session für {phone_number} bereinigt")
    
    def get_active_sessions_count(self) -> int:
        """Anzahl aktiver Sessions"""
        return len(self.active_sessions)
    
    def get_all_sessions(self) -> List[Dict]:
        """Alle Sessions auflisten"""
        return [
            {
                "phone_number": phone,
                "status": info["status"],
                "created_at": info["created_at"],
                "activated_at": info.get("activated_at")
            }
            for phone, info in self.session_data.items()
        ]
