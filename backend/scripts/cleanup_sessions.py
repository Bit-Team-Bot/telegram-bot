#!/usr/bin/env python3
"""
Cleanup Script für abgelaufene Sessions
Sollte regelmäßig als Cron-Job ausgeführt werden
"""

import sys
import os
from datetime import datetime

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.utils.sessions import cleanup_expired_sessions
import logging

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Hauptfunktion für das Cleanup-Script"""
    logger.info("🔄 Starte Session-Cleanup...")
    
    try:
        # Datenbankverbindung erstellen
        db = SessionLocal()
        
        # Abgelaufene Sessions bereinigen
        cleaned_count = cleanup_expired_sessions(db)
        
        logger.info(f"✅ Cleanup abgeschlossen: {cleaned_count} Sessions bereinigt")
        
        # Datenbankverbindung schließen
        db.close()
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Session-Cleanup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 