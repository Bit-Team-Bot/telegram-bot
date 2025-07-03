# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API Credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "https://api.bit-team-bot.online")

# Userbot-Service URL
USERBOT_SERVICE_URL = os.getenv("USERBOT_SERVICE_URL", "http://localhost:9000")

# Frontend URL
WEBUI_URL = os.getenv("WEBUI_URL", "https://webui.bit-team-bot.online")

# Session Name
SESSION_NAME = os.getenv("SESSION_NAME", "bit_team_session")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Admin Chat ID für Benachrichtigungen
ADMIN_CHAT_ID = None
