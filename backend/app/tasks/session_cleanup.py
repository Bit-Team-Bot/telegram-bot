from app.database import SessionLocal
from app.utils.sessions import cleanup_expired_sessions
import logging

def run_daily_maintenance():
    """
    Führt tägliche Wartungsaufgaben aus (Session-Cleanup).
    """
    logging.info("Starte tägliche Wartung: Session-Cleanup...")
    db = SessionLocal()
    try:
        cleaned_count = cleanup_expired_sessions(db)
        logging.info(f"{cleaned_count} abgelaufene Sessions bereinigt.")
    except Exception as e:
        logging.error(f"Fehler beim Session-Cleanup: {e}")
    finally:
        db.close() 