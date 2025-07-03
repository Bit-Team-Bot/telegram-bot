#!/usr/bin/env python3
"""
Migration Script für Signalgruppen-Preis-Felder
Fügt die neuen Preis-Felder zur signal_groups Tabelle hinzu
"""

import sqlite3
import sys
import os

# Pfad zur Datenbank
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'telegram_bot.db')

def migrate_signal_groups():
    """Fügt Preis-Felder zur signal_groups Tabelle hinzu"""
    print("🔄 Migriere Signalgruppen-Tabelle...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Prüfe ob die Felder bereits existieren
        cursor.execute("PRAGMA table_info(signal_groups)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Neue Felder hinzufügen falls sie nicht existieren
        new_columns = [
            ('price_1_group', 'REAL DEFAULT 0.0'),
            ('price_2_groups', 'REAL DEFAULT 0.0'),
            ('price_3_groups', 'REAL DEFAULT 0.0'),
            ('price_4_groups', 'REAL DEFAULT 0.0'),
            ('price_5_groups', 'REAL DEFAULT 0.0'),
            ('updated_at', 'DATETIME DEFAULT CURRENT_TIMESTAMP')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                print(f"  ➕ Füge Spalte '{column_name}' hinzu...")
                cursor.execute(f"ALTER TABLE signal_groups ADD COLUMN {column_name} {column_type}")
            else:
                print(f"  ✅ Spalte '{column_name}' existiert bereits")
        
        # Beispieldaten für Signalgruppen erstellen falls keine vorhanden sind
        cursor.execute("SELECT COUNT(*) FROM signal_groups")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("  📝 Erstelle Beispieldaten für Signalgruppen...")
            
            sample_groups = [
                {
                    'name': 'BTC-Signale Premium',
                    'description': 'Exklusive Bitcoin-Signale mit hoher Erfolgsquote',
                    'price_1_group': 29.99,
                    'price_2_groups': 54.99,
                    'price_3_groups': 79.99,
                    'price_4_groups': 99.99,
                    'price_5_groups': 119.99
                },
                {
                    'name': 'Altcoin-Signale',
                    'description': 'Signale für Altcoins und DeFi-Token',
                    'price_1_group': 19.99,
                    'price_2_groups': 34.99,
                    'price_3_groups': 49.99,
                    'price_4_groups': 64.99,
                    'price_5_groups': 79.99
                },
                {
                    'name': 'VIP-Signale',
                    'description': 'Exklusive VIP-Signale mit maximaler Priorität',
                    'price_1_group': 49.99,
                    'price_2_groups': 89.99,
                    'price_3_groups': 129.99,
                    'price_4_groups': 159.99,
                    'price_5_groups': 189.99
                }
            ]
            
            for group in sample_groups:
                cursor.execute("""
                    INSERT INTO signal_groups 
                    (name, description, price_1_group, price_2_groups, price_3_groups, price_4_groups, price_5_groups, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    group['name'],
                    group['description'],
                    group['price_1_group'],
                    group['price_2_groups'],
                    group['price_3_groups'],
                    group['price_4_groups'],
                    group['price_5_groups'],
                    True
                ))
                print(f"    ✅ {group['name']} erstellt")
        
        conn.commit()
        print("✅ Signalgruppen-Migration erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_signal_groups() 