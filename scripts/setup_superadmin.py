#!/usr/bin/env python3
"""
Script zum Einrichten eines Superusers
"""

import sqlite3
import sys
from pathlib import Path

def setup_superadmin(telegram_id: str, db_path: str = "backend/telegram_bot.db"):
    """Richtet einen Superuser ein"""
    
    try:
        # Datenbankverbindung
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob User existiert
        cursor.execute("SELECT id, user_name, is_superadmin FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User mit Telegram-ID {telegram_id} nicht gefunden!")
            print("💡 Tipp: Starte zuerst den Bot und führe /start aus, um den User anzulegen.")
            return False
        
        user_id, user_name, is_superadmin = user
        
        if is_superadmin:
            print(f"✅ User {user_name} (ID: {user_id}) ist bereits Superadmin!")
            return True
        
        # Superadmin-Rechte vergeben
        cursor.execute("""
            UPDATE users 
            SET is_superadmin = 1, role = 'superadmin' 
            WHERE telegram_id = ?
        """, (telegram_id,))
        
        conn.commit()
        
        print(f"✅ User {user_name} (ID: {user_id}) erfolgreich als Superadmin eingerichtet!")
        print(f"   Telegram-ID: {telegram_id}")
        print(f"   Role: superadmin")
        print(f"   is_superadmin: 1")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Einrichten des Superusers: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def list_users(db_path: str = "backend/telegram_bot.db"):
    """Listet alle User auf"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, telegram_id, user_name, phone, is_superadmin, role, created_at 
            FROM users 
            ORDER BY id
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("📋 Keine User in der Datenbank gefunden.")
            return
        
        print("📋 User in der Datenbank:")
        print("-" * 80)
        print(f"{'ID':<3} {'Telegram-ID':<15} {'Name':<15} {'Phone':<15} {'Admin':<5} {'Role':<10} {'Created'}")
        print("-" * 80)
        
        for user in users:
            user_id, telegram_id, user_name, phone, is_superadmin, role, created_at = user
            admin_status = "✅" if is_superadmin else "❌"
            print(f"{user_id:<3} {telegram_id:<15} {user_name or 'N/A':<15} {phone or 'N/A':<15} {admin_status:<5} {role:<10} {created_at}")
        
    except Exception as e:
        print(f"❌ Fehler beim Auflisten der User: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Hauptfunktion"""
    
    if len(sys.argv) < 2:
        print("🔧 Superuser Setup Tool")
        print("=" * 40)
        print()
        print("Verwendung:")
        print(f"  {sys.argv[0]} setup <telegram_id>  - Superuser einrichten")
        print(f"  {sys.argv[0]} list                 - Alle User auflisten")
        print()
        print("Beispiele:")
        print(f"  {sys.argv[0]} setup 5719897345")
        print(f"  {sys.argv[0]} list")
        return
    
    command = sys.argv[1]
    
    if command == "setup":
        if len(sys.argv) < 3:
            print("❌ Telegram-ID erforderlich!")
            print(f"Verwendung: {sys.argv[0]} setup <telegram_id>")
            return
        
        telegram_id = sys.argv[2]
        setup_superadmin(telegram_id)
        
    elif command == "list":
        list_users()
        
    else:
        print(f"❌ Unbekannter Befehl: {command}")
        print("Verfügbare Befehle: setup, list")

if __name__ == "__main__":
    main() 