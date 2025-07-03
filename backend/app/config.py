import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Lade .env aus dem Projekt-Root (2 Verzeichnisse nach oben)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'))

class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Datenbank
    DATABASE_URL: str = "sqlite:///./telegram_bot.db"
    DB_TYPE: str = "sqlite"
    
    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 Tage
    
    # Telegram
    BOT_TOKEN: Optional[str] = None
    TELEGRAM_WEBAPP_SECRET: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: str = "https://webui.bit-team-bot.online,https://api.bit-team-bot.online"
    
    # Blockchain
    BSC_RPC_URL: str = "https://bsc-dataseed1.binance.org/"
    BOT_WALLET: str = ""
    BOT_WALLET_PK: str = ""
    
    # Userbot Service
    USERBOT_URL: str = "http://localhost:8001"
    USERBOT_API_URL: str = "http://localhost:8001"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignoriere zusätzliche Felder in .env

settings = Settings()
