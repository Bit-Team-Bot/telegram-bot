#!/usr/bin/env python3
"""
Cleanup Script für Paket-Templates
Löscht inaktive Templates und behält nur die wirklich vorhandenen
"""

import sqlite3
import sys
import os

# Pfad zur Datenbank
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'telegram_bot.db')

def cleanup_templates():
    """Bereinigt die Paket-Templates"""
    print("🧹 Bereinige Paket-Templates...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Aktuelle Templates anzeigen
        cursor.execute("SELECT id, name, display_name, is_active FROM package_templates")
        templates = cursor.fetchall()
        
        print(f"📋 Gefundene Templates: {len(templates)}")
        for template in templates:
            status = "✅ Aktiv" if template[3] else "❌ Inaktiv"
            print(f"  {template[0]}: {template[2]} ({template[1]}) - {status}")
        
        # Inaktive Templates löschen
        cursor.execute("DELETE FROM package_templates WHERE is_active = 0")
        deleted_count = cursor.rowcount
        
        if deleted_count > 0:
            print(f"🗑️ {deleted_count} inaktive Templates gelöscht")
        else:
            print("✅ Keine inaktiven Templates gefunden")
        
        # Verbleibende Templates anzeigen
        cursor.execute("SELECT id, name, display_name, is_active FROM package_templates")
        remaining_templates = cursor.fetchall()
        
        print(f"\n📋 Verbleibende Templates: {len(remaining_templates)}")
        for template in remaining_templates:
            print(f"  ✅ {template[2]} ({template[1]})")
        
        # Standard-Templates erstellen falls keine vorhanden sind
        if len(remaining_templates) == 0:
            print("\n📝 Erstelle Standard-Templates...")
            
            standard_templates = [
                {
                    'name': 'starter',
                    'display_name': 'Starter',
                    'package_type': 'starter',
                    'monthly_price': 49.99,
                    'one_time_price': None,
                    'features': '{"message_forwarding_basic": true, "group_management_basic": true, "signal_groups_basic": true}'
                },
                {
                    'name': 'pro',
                    'display_name': 'Pro',
                    'package_type': 'pro',
                    'monthly_price': 99.99,
                    'one_time_price': None,
                    'features': '{"message_forwarding_pro": true, "group_management_pro": true, "signal_groups_pro": true}'
                },
                {
                    'name': 'expert',
                    'display_name': 'Expert',
                    'package_type': 'expert',
                    'monthly_price': 199.99,
                    'one_time_price': None,
                    'features': '{"message_forwarding_expert": true, "group_management_expert": true, "signal_groups_expert": true}'
                },
                {
                    'name': 'lifetime',
                    'display_name': 'Lifetime',
                    'package_type': 'lifetime',
                    'monthly_price': None,
                    'one_time_price': 999.99,
                    'features': '{"message_forwarding_expert": true, "group_management_expert": true, "signal_groups_expert": true}'
                }
            ]
            
            for template in standard_templates:
                cursor.execute("""
                    INSERT INTO package_templates 
                    (name, display_name, package_type, monthly_price, one_time_price, features, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    template['name'],
                    template['display_name'],
                    template['package_type'],
                    template['monthly_price'],
                    template['one_time_price'],
                    template['features'],
                    True
                ))
                print(f"    ✅ {template['display_name']} erstellt")
        
        conn.commit()
        print("\n✅ Template-Bereinigung erfolgreich abgeschlossen!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Bereinigung: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup_templates() 