import os
from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv

# Zentrale .env aus Projekt-Root laden
load_dotenv(dotenv_path="/home/manny/telegram-bot/.env")

port_str = os.getenv("PORT")

class Settings(BaseSettings):
    HOST: Optional[str] = os.getenv("HOST")
    PORT: Optional[int] = int(port_str) if port_str and port_str.isdigit() else None
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    JWT_SECRET: Optional[str] = os.getenv("JWT_SECRET")
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    USERBOT_URL: Optional[str] = os.getenv("USERBOT_URL")
    WEBUI_URL: Optional[str] = os.getenv("WEBUI_URL")
    LOG_LEVEL: Optional[str] = os.getenv("LOG_LEVEL")
    ENVIRONMENT: Optional[str] = os.getenv("ENVIRONMENT")
    ALGORITHM: str = "HS256"

    class Config:
        env_file = "/home/manny/telegram-bot/.env"
        extra = "ignore"

settings = Settings()
