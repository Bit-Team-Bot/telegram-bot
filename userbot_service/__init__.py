"""
Userbot-Service Modul

Dieses Modul bietet:
- Telegram-Session-Handling pro Telefonnummer
- Senden und Prüfen von Login-Codes via Telegram
- Verknüpfung von WebUI-Login und Userbot-Session
- Fehlerbehandlung und Session-Verwaltung
"""

from .userbot_manager import UserbotManager

__all__ = [
    'UserbotManager'
]
