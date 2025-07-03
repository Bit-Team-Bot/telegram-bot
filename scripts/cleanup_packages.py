#!/usr/bin/env python3
"""
Skript zum Aufräumen der Paket-Datenbank
Entfernt Duplikate und bereitet die neue Feature-Matrix vor
"""

import sqlite3
import json
from datetime import datetime

def cleanup_database():
    """Bereinigt die Datenbank von Duplikaten und bereitet neue Struktur vor"""
    
    conn = sqlite3.connect('backend/telegram_bot.db')
    cursor = conn.cursor()
    
    print("🧹 Bereinige Paket-Datenbank...")
    
    # 1. Backup erstellen
    cursor.execute("CREATE TABLE IF NOT EXISTS packages_backup AS SELECT * FROM packages")
    print("✅ Backup der bestehenden Pakete erstellt")
    
    # 2. Doppelte Pakete finden und entfernen
    cursor.execute("""
        DELETE FROM packages 
        WHERE id NOT IN (
            SELECT MIN(id) 
            FROM packages 
            GROUP BY name
        )
    """)
    print("✅ Doppelte Pakete entfernt")
    
    # 3. Bestehende Pakete löschen (wir erstellen neue)
    cursor.execute("DELETE FROM packages")
    print("✅ Bestehende Pakete gelöscht")
    
    # 4. Package Templates löschen
    cursor.execute("DELETE FROM package_templates")
    print("✅ Package Templates gelöscht")
    
    # 5. Addons löschen
    cursor.execute("DELETE FROM addons")
    print("✅ Addons gelöscht")
    
    # 6. Addon Tiers löschen
    cursor.execute("DELETE FROM addon_tiers")
    print("✅ Addon Tiers gelöscht")
    
    # 7. Package Addons löschen
    cursor.execute("DELETE FROM package_addons")
    print("✅ Package Addons gelöscht")
    
    # 8. User Addons löschen
    cursor.execute("DELETE FROM user_addons")
    print("✅ User Addons gelöscht")
    
    conn.commit()
    conn.close()
    
    print("✅ Datenbank-Bereinigung abgeschlossen")

if __name__ == "__main__":
    cleanup_database() 