import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API Credentials
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME")

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL")
USERBOT_URL = os.getenv("USERBOT_URL")

# Service Configuration
port_str = os.getenv("SERVICE_PORT")
SERVICE_HOST = os.getenv("SERVICE_HOST")
SERVICE_PORT = int(port_str) if port_str and port_str.isdigit() else None

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL")

DATABASE_URL = os.getenv("DATABASE_URL")
