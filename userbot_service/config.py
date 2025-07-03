import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API Credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = "bit_team_session"

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "https://api.bit-team-bot.online")

# Service Configuration
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 9000))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
