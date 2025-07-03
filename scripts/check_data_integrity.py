#!/usr/bin/env python3
"""
Datenintegritätsprüfung für Telegram Bot System
Prüft die Konsistenz zwischen Bot, Backend und WebUI
"""

import requests
import json
import sqlite3
from datetime import datetime
import sys

# Konfiguration
BACKEND_URL = "http://localhost:8000"
DB_PATH = "backend/telegram_bot.db"

def check_backend_api():
    """Prüft Backend-API und User-Daten"""
    try:
        response = requests.get(f"{BACKEND_URL}/users/users/test/integrity", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Backend-API Fehler: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Backend-API nicht erreichbar: {e}")
        return None

def check_database_directly():
    """Prüft Datenbank direkt"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # User zählen
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # User ohne Telegram-ID
        cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NULL")
        users_without_telegram_id = cursor.fetchone()[0]
        
        # User mit Telefonnummer aber ohne Telegram-ID
        cursor.execute("SELECT COUNT(*) FROM users WHERE telegram_id IS NULL AND phone IS NOT NULL")
        users_phone_no_telegram = cursor.fetchone()[0]
        
        # Alle User-Daten
        cursor.execute("""
            SELECT id, telegram_id, phone, user_name, is_active, created_at 
            FROM users 
            ORDER BY id
        """)
        users = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_users": total_users,
            "users_without_telegram_id": users_without_telegram_id,
            "users_phone_no_telegram": users_phone_no_telegram,
            "users": users
        }
    except Exception as e:
        print(f"❌ Datenbank-Fehler: {e}")
        return None

def generate_report():
    """Generiert einen vollständigen Bericht"""
    print("🔍 DATENINTEGRITÄTSPRÜFUNG")
    print("=" * 50)
    print(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Backend-API prüfen
    print("📡 Backend-API Status:")
    api_data = check_backend_api()
    if api_data:
        print(f"✅ Backend erreichbar")
        print(f"   Total Users (API): {api_data.get('total_users', 0)}")
        print(f"   Database Path: {api_data.get('database_path', 'unknown')}")
        
        # User-Details aus API
        users = api_data.get('users', [])
        users_without_telegram = [u for u in users if not u.get('telegram_id')]
        if users_without_telegram:
            print(f"   ⚠️  Users ohne Telegram-ID: {len(users_without_telegram)}")
        else:
            print(f"   ✅ Alle User haben Telegram-IDs")
    else:
        print("❌ Backend nicht erreichbar")
    
    print()
    
    # Direkte Datenbankprüfung
    print("🗄️  Direkte Datenbankprüfung:")
    db_data = check_database_directly()
    if db_data:
        print(f"✅ Datenbank erreichbar")
        print(f"   Total Users (DB): {db_data['total_users']}")
        print(f"   Users ohne Telegram-ID: {db_data['users_without_telegram_id']}")
        print(f"   Users mit Phone aber ohne Telegram-ID: {db_data['users_phone_no_telegram']}")
        
        if db_data['users_phone_no_telegram'] > 0:
            print("   ⚠️  PROBLEM: User mit Telefonnummer aber ohne Telegram-ID gefunden!")
            print("   💡 Empfehlung: Diese User bereinigen oder Telegram-ID verknüpfen")
        
        # User-Details
        print("\n📋 User-Details:")
        for user in db_data['users']:
            user_id, telegram_id, phone, user_name, is_active, created_at = user
            status = "✅" if telegram_id else "❌"
            print(f"   {status} ID: {user_id}, TG: {telegram_id or 'NULL'}, Phone: {phone or 'NULL'}, Name: {user_name or 'NULL'}")
    else:
        print("❌ Datenbank nicht erreichbar")
    
    print()
    
    # Zusammenfassung
    print("📊 ZUSAMMENFASSUNG:")
    if api_data and db_data:
        api_users = api_data.get('total_users', 0)
        db_users = db_data['total_users']
        
        if api_users == db_users:
            print("✅ API und Datenbank sind synchron")
        else:
            print(f"❌ Inkonsistenz: API={api_users}, DB={db_users}")
        
        if db_data['users_phone_no_telegram'] == 0:
            print("✅ Keine inkonsistenten User-Datensätze")
        else:
            print(f"⚠️  {db_data['users_phone_no_telegram']} inkonsistente User-Datensätze")
    else:
        print("❌ Vollständige Prüfung nicht möglich")
    
    print("=" * 50)

def main():
    """Hauptfunktion"""
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        # JSON-Output für automatisierte Verarbeitung
        api_data = check_backend_api()
        db_data = check_database_directly()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "api_data": api_data,
            "db_data": db_data,
            "status": "ok" if api_data and db_data else "error"
        }
        
        print(json.dumps(result, indent=2))
    else:
        # Menschlich lesbarer Bericht
        generate_report()

if __name__ == "__main__":
    main() 