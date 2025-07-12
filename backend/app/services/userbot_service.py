"""
Zentraler Userbot-Service für das Backend
Vereinigt alle Userbot-Funktionalität in einem Service
"""

import httpx
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Lade .env aus Root-Verzeichnis
root_dir = Path(__file__).parent.parent.parent.parent
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

class UserbotService:
    """Zentraler Service für Userbot-Operationen"""
    
    def __init__(self):
        self.userbot_api_url = os.getenv("USERBOT_URL", "http://localhost:8001")
        self.timeout = 30.0
        
    async def create_session(self, phone_number: str) -> Dict:
        """Neue Userbot-Session erstellen"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.userbot_api_url}/manager/create_session",
                    json={"phone_number": phone_number}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Erstellen der Session für {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_code(self, phone_number: str) -> Dict:
        """Verifizierungscode senden"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.userbot_api_url}/manager/send_code",
                    json={"phone_number": phone_number}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Senden des Codes für {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_code(self, phone_number: str, code: str, password: Optional[str] = None) -> Dict:
        """Code verifizieren"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "phone_number": phone_number,
                    "code": code
                }
                if password:
                    payload["password"] = password
                    
                response = await client.post(
                    f"{self.userbot_api_url}/manager/verify_code",
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler bei der Code-Verifikation für {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_session_status(self, phone_number: str) -> Dict:
        """Session-Status abrufen"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.userbot_api_url}/manager/session_status/{phone_number}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Session-Status für {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def disconnect_session(self, phone_number: str) -> Dict:
        """Session trennen"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.userbot_api_url}/manager/disconnect_session",
                    json={"phone_number": phone_number}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Trennen der Session für {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_chats(self, phone_number: str) -> Dict:
        """Chats für Session abrufen"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.userbot_api_url}/manager/chats/{phone_number}"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Chats für {phone_number}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_active_sessions_count(self) -> Dict:
        """Anzahl aktiver Sessions abrufen"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.userbot_api_url}/manager/active_sessions_count"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der aktiven Sessions: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_all_sessions(self) -> Dict:
        """Alle Sessions abrufen"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.userbot_api_url}/manager/all_sessions"
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Fehler beim Abrufen aller Sessions: {e}")
            return {"success": False, "error": str(e)}

# Globale Instanz
userbot_service = UserbotService() 