from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pathlib import Path
import os
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()

# Projektverzeichnis automatisch erkennen
BASE_DIR = Path(__file__).resolve().parent.parent

# Datenbank-URL immer aus DATABASE_URL lesen
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/telegram_bot.db")

# Engine bauen
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def init_db():
    # Base.metadata.create_all wird in main.py aufgerufen
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()