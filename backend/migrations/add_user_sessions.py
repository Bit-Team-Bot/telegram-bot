"""
Migration: Add user_sessions table
"""

import sys
import os
from datetime import datetime

# Füge das Backend-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import UserSession
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Führt die Migration aus"""
    print("🔄 Erstelle user_sessions Tabelle...")
    
    try:
        # Erstelle die Tabelle
        Base.metadata.create_all(bind=engine, tables=[UserSession.__table__])
        print("✅ user_sessions Tabelle erfolgreich erstellt!")
        
        # Teste die Verbindung
        from app.database import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ Datenbankverbindung erfolgreich getestet!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {str(e)}")
        raise

if __name__ == "__main__":
    migrate() 