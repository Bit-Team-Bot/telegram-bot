# config.py
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Finde das Root-Verzeichnis (ein Verzeichnis über bot/)
root_dir = Path(__file__).parent.parent
env_file = root_dir / ".env"

# Lade .env aus dem Root-Verzeichnis
if env_file.exists():
    load_dotenv(env_file)
else:
    # Fallback: versuche .env im aktuellen Verzeichnis
    load_dotenv()

# Telegram API Credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL")

# Userbot-Service URL
USERBOT_URL = os.getenv("USERBOT_URL")

# Frontend URL
WEBUI_URL = os.getenv("WEBUI_URL")

# Session Name
SESSION_NAME = os.getenv("SESSION_NAME")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL")

# Admin Chat ID für Benachrichtigungen
ADMIN_CHAT_ID = None

JWT_SECRET = os.getenv("JWT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")