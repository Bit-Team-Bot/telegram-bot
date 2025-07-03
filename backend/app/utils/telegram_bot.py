import httpx
import logging
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)

async def send_telegram_message(chat_id: str, message: str, parse_mode: str = "HTML") -> bool:
    """
    Sendet eine Nachricht über den Telegram Bot
    """
    try:
        if not settings.BOT_TOKEN:
            logger.warning("Telegram Bot Token nicht konfiguriert")
            return False
        
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode
            })
            
            if response.status_code == 200:
                logger.info(f"Nachricht erfolgreich an {chat_id} gesendet")
                return True
            else:
                logger.error(f"Fehler beim Senden der Nachricht: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Fehler beim Senden der Telegram-Nachricht: {e}")
        return False

async def get_telegram_user_info(user_id: str) -> Optional[dict]:
    """
    Holt Informationen über einen Telegram-Benutzer
    """
    try:
        if not settings.BOT_TOKEN:
            logger.warning("Telegram Bot Token nicht konfiguriert")
            return None
        
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChat"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={
                "chat_id": user_id
            })
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    return data.get("result")
            
            logger.error(f"Fehler beim Abrufen der Benutzerinformationen: {response.status_code}")
            return None
                
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Telegram-Benutzerinformationen: {e}")
        return None

async def send_telegram_notification(chat_id: str, title: str, message: str, notification_type: str = "info") -> bool:
    """
    Sendet eine formatierte Benachrichtigung
    """
    try:
        # Emoji basierend auf Typ
        emoji_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        
        emoji = emoji_map.get(notification_type, "ℹ️")
        
        formatted_message = f"{emoji} <b>{title}</b>\n\n{message}"
        
        return await send_telegram_message(chat_id, formatted_message)
        
    except Exception as e:
        logger.error(f"Fehler beim Senden der Benachrichtigung: {e}")
        return False 