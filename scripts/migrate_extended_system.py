#!/usr/bin/env python3
"""
Migration Script für erweitertes Signalgruppen- und Userbot-System
Fügt neue Felder und Tabellen hinzu
"""

import sqlite3
import sys
import os

# Pfad zur Datenbank
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'telegram_bot.db')

def migrate_extended_system():
    """Migriert das System um erweiterte Signalgruppen und Userbot-Funktionen"""
    print("🔄 Migriere erweitertes System...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. Signalgruppen-Tabelle erweitern
        print("📡 Erweitere Signalgruppen-Tabelle...")
        
        # Neue Spalten für signal_groups
        new_columns = [
            ('source_group_id', 'TEXT'),
            ('created_group_id', 'TEXT'),
            ('created_group_invite_link', 'TEXT'),
            ('theme', 'TEXT')
        ]
        
        cursor.execute("PRAGMA table_info(signal_groups)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                print(f"  ➕ Füge Spalte '{column_name}' hinzu...")
                cursor.execute(f"ALTER TABLE signal_groups ADD COLUMN {column_name} {column_type}")
            else:
                print(f"  ✅ Spalte '{column_name}' existiert bereits")
        
        # 2. Userbot-Sessions-Tabelle erstellen
        print("🤖 Erstelle Userbot-Sessions-Tabelle...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS userbot_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                phone TEXT NOT NULL,
                session_name TEXT NOT NULL,
                session_type TEXT NOT NULL,
                telegram_session_string TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # 3. Signalgruppen-Abonnements-Tabelle erstellen
        print("📋 Erstelle Signalgruppen-Abonnements-Tabelle...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS signal_group_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                signal_group_id INTEGER NOT NULL,
                group_count INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (signal_group_id) REFERENCES signal_groups (id)
            )
        """)
        
        # 4. Beispieldaten für erweiterte Signalgruppen
        print("📝 Aktualisiere Beispieldaten...")
        
        # Aktualisiere bestehende Signalgruppen mit Themen
        cursor.execute("""
            UPDATE signal_groups 
            SET theme = 'Bitcoin-Signale' 
            WHERE name = 'BTC-Signale Premium'
        """)
        
        cursor.execute("""
            UPDATE signal_groups 
            SET theme = 'Altcoin-Signale' 
            WHERE name = 'Altcoin-Signale'
        """)
        
        cursor.execute("""
            UPDATE signal_groups 
            SET theme = 'VIP-Signale' 
            WHERE name = 'VIP-Signale'
        """)
        
        # 5. Beispieldaten für Userbot-Sessions
        print("🤖 Erstelle Beispieldaten für Userbot-Sessions...")
        
        # Prüfe ob bereits Sessions existieren
        cursor.execute("SELECT COUNT(*) FROM userbot_sessions")
        session_count = cursor.fetchone()[0]
        
        if session_count == 0:
            # Erstelle Beispieldaten für Userbot-Sessions
            sample_sessions = [
                {
                    'user_id': 1,  # Erster User
                    'phone': '+49123456789',
                    'session_name': 'Meine Weiterleitungen',
                    'session_type': 'message_forwarding',
                    'is_active': True
                },
                {
                    'user_id': 1,
                    'phone': '+49123456789',
                    'session_name': 'Signal-Gruppen Bot',
                    'session_type': 'signal_groups',
                    'is_active': True
                }
            ]
            
            for session in sample_sessions:
                cursor.execute("""
                    INSERT INTO userbot_sessions 
                    (user_id, phone, session_name, session_type, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    session['user_id'],
                    session['phone'],
                    session['session_name'],
                    session['session_type'],
                    session['is_active']
                ))
                print(f"    ✅ {session['session_name']} erstellt")
        
        # 6. Beispieldaten für Signalgruppen-Abonnements
        print("📋 Erstelle Beispieldaten für Abonnements...")
        
        cursor.execute("SELECT COUNT(*) FROM signal_group_subscriptions")
        subscription_count = cursor.fetchone()[0]
        
        if subscription_count == 0:
            # Erstelle Beispieldaten für Abonnements
            sample_subscriptions = [
                {
                    'user_id': 1,
                    'signal_group_id': 1,  # BTC-Signale Premium
                    'group_count': 2,
                    'status': 'active'
                },
                {
                    'user_id': 1,
                    'signal_group_id': 2,  # Altcoin-Signale
                    'group_count': 1,
                    'status': 'active'
                }
            ]
            
            for subscription in sample_subscriptions:
                cursor.execute("""
                    INSERT INTO signal_group_subscriptions 
                    (user_id, signal_group_id, group_count, status, start_date, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    subscription['user_id'],
                    subscription['signal_group_id'],
                    subscription['group_count'],
                    subscription['status']
                ))
                print(f"    ✅ Abonnement für User {subscription['user_id']} erstellt")
        
        conn.commit()
        print("\n✅ Erweiterte System-Migration erfolgreich abgeschlossen!")
        
        # Zeige Zusammenfassung
        print("\n📊 Migration-Zusammenfassung:")
        cursor.execute("SELECT COUNT(*) FROM signal_groups")
        signal_groups_count = cursor.fetchone()[0]
        print(f"  - Signalgruppen: {signal_groups_count}")
        
        cursor.execute("SELECT COUNT(*) FROM userbot_sessions")
        sessions_count = cursor.fetchone()[0]
        print(f"  - Userbot-Sessions: {sessions_count}")
        
        cursor.execute("SELECT COUNT(*) FROM signal_group_subscriptions")
        subscriptions_count = cursor.fetchone()[0]
        print(f"  - Abonnements: {subscriptions_count}")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_extended_system() 