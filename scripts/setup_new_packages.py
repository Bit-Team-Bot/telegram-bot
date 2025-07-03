#!/usr/bin/env python3
"""
Skript zur Einrichtung der neuen Paketstruktur
Basierend auf der erweiterten Masterliste mit allen Features
"""

import sqlite3
import json
from datetime import datetime

def setup_new_packages():
    """Erstellt die neue Paketstruktur mit allen Features"""
    
    conn = sqlite3.connect('backend/telegram_bot.db')
    cursor = conn.cursor()
    
    print("🚀 Erstelle neue Paketstruktur...")
    
    # 1. Feature-Matrix definieren (alle Features aus der Masterliste)
    feature_matrix = {
        # Nachrichten-Weiterleitung
        "message_forwarding_basic": {
            "name": "Nachrichten-Weiterleitung (Basic)",
            "description": "1 Quell- & 1 Zielgruppe, Basis-Keywordfilter",
            "category": "message_forwarding"
        },
        "message_forwarding_pro": {
            "name": "Nachrichten-Weiterleitung (Pro)",
            "description": "Bis 5 Quell- & Zielgruppen, Keyword- und Userfilter, Medienanhänge",
            "category": "message_forwarding"
        },
        "message_forwarding_expert": {
            "name": "Nachrichten-Weiterleitung (Expert)",
            "description": "Unbegrenzt Gruppen, Filterlogik (Regex, User, Inhalt), Auto-Übersetzung, Priorisierung",
            "category": "message_forwarding"
        },
        "time_scheduled_forwarding": {
            "name": "Zeitgesteuerte Weiterleitung",
            "description": "Scheduler pro Gruppe",
            "category": "message_forwarding_addon"
        },
        "text_replacement_rules": {
            "name": "Ersetzungsregeln",
            "description": "Text vor Versand ändern",
            "category": "message_forwarding_addon"
        },
        "duplicate_filter": {
            "name": "Duplicate-Filter",
            "description": "Keine doppelten Weiterleitungen",
            "category": "message_forwarding_addon"
        },
        "webhook_triggered_messages": {
            "name": "Webhook für ausgelöste Nachrichten",
            "description": "Webhook-Integration für Nachrichten",
            "category": "message_forwarding_addon"
        },
        "message_statistics": {
            "name": "Nachrichten-Statistiken",
            "description": "Statistiken pro Weiterleitungsregel",
            "category": "message_forwarding_addon"
        },
        "anonymous_forwarding": {
            "name": "Anonymisierte Weiterleitung",
            "description": "Kein Username/ID in weitergeleiteten Nachrichten",
            "category": "message_forwarding_addon"
        },
        
        # Gruppenverwaltung
        "group_management_basic": {
            "name": "Gruppenverwaltung (Basic)",
            "description": "Gruppenübersicht, manuelles Hinzufügen/Entfernen",
            "category": "group_management"
        },
        "group_management_pro": {
            "name": "Gruppenverwaltung (Pro)",
            "description": "Sync Telegram ↔ WebUI, Admin-Rechte im UI",
            "category": "group_management"
        },
        "group_management_expert": {
            "name": "Gruppenverwaltung (Expert)",
            "description": "Gruppen automatisch erstellen, Auto-Mitgliederhandling, Eigentümer-Verwaltung",
            "category": "group_management"
        },
        "auto_group_welcome": {
            "name": "Automatisierte Gruppen-Begrüßung",
            "description": "Automatische Begrüßung neuer Mitglieder",
            "category": "group_management_addon"
        },
        "invite_link_generator": {
            "name": "Invite-Link-Generator",
            "description": "Direkt im WebUI",
            "category": "group_management_addon"
        },
        "group_backup_restore": {
            "name": "Gruppen-Backup & Restore",
            "description": "Archivierung von Gruppen",
            "category": "group_management_addon"
        },
        "user_limit_per_group": {
            "name": "Limitierung auf X User pro Gruppe",
            "description": "Automatische Begrenzung der Gruppenmitglieder",
            "category": "group_management_addon"
        },
        "auto_kick_bots_spam": {
            "name": "Automatisches Kick/Ban von Bots/Spam",
            "description": "Automatische Spam-Erkennung und -Entfernung",
            "category": "group_management_addon"
        },
        
        # Signalgruppen / VIP-Signale
        "signal_groups_basic": {
            "name": "Signalgruppen (Basic)",
            "description": "1 Signalgruppe, manuelle Weiterleitung",
            "category": "signal_groups"
        },
        "signal_groups_pro": {
            "name": "Signalgruppen (Pro)",
            "description": "Bis 5 Gruppen, Automatisierte Weiterleitung, Zeitplan/Trigger",
            "category": "signal_groups"
        },
        "signal_groups_expert": {
            "name": "Signalgruppen (Expert)",
            "description": "Unbegrenzt, Signal-Mapping, VIP-Automation",
            "category": "signal_groups"
        },
        "performance_tracking": {
            "name": "Performance-Tracking",
            "description": "Performance-Tracking für jedes Signal",
            "category": "signal_groups_addon"
        },
        "signal_notifications": {
            "name": "Signal-Benachrichtigungen",
            "description": "Push, Telegram, E-Mail für neue Signale",
            "category": "signal_groups_addon"
        },
        "individual_notification_settings": {
            "name": "Individuelle Benachrichtigungseinstellungen",
            "description": "Pro User konfigurierbar",
            "category": "signal_groups_addon"
        },
        "external_signal_api": {
            "name": "API für externe Signal-Anbieter",
            "description": "API-Integration für externe Signalquellen",
            "category": "signal_groups_addon"
        },
        
        # Sonstige Funktionen / Addons
        "multi_language_support": {
            "name": "Multi-Language Support",
            "description": "DE, EN, RU, TR, IT",
            "category": "general_addon"
        },
        "darkmode_webui": {
            "name": "Darkmode für WebUI",
            "description": "Darkmode-Unterstützung",
            "category": "general_addon"
        },
        "usdt_billing": {
            "name": "USDT-Abrechnung",
            "description": "Abrechnung in USDT",
            "category": "billing"
        },
        "lifetime_monthly_model": {
            "name": "Lifetime/Monatsmodell",
            "description": "Flexible Abrechnungsmodelle",
            "category": "billing"
        },
        "auto_invoice_email": {
            "name": "Automatische Rechnungserstellung",
            "description": "Per E-Mail",
            "category": "billing_addon"
        },
        "user_management": {
            "name": "Benutzerverwaltung",
            "description": "Manuell & automatisch, Rechte pro Paket & Rolle",
            "category": "admin"
        },
        "bot_admin_panel": {
            "name": "Bot-Admin-Panel",
            "description": "Admin-Panel für Bot-Verwaltung",
            "category": "admin"
        },
        "api_webhooks": {
            "name": "API/Webhooks",
            "description": "API-Zugriff und Webhook-Integration",
            "category": "api"
        },
        "media_forwarding": {
            "name": "Medienweiterleitung",
            "description": "Erweiterte Medienweiterleitung",
            "category": "media"
        },
        "advanced_filter_logic": {
            "name": "Erweiterte Filterlogik",
            "description": "Regex/User/Blacklist",
            "category": "filtering"
        },
        "custom_package_upgrades": {
            "name": "Benutzerdefinierte Paket-Upgrades",
            "description": "Per Klick statt Support",
            "category": "ui_addon"
        },
        "free_trial_7_days": {
            "name": "7 Tage Free Trial",
            "description": "Zeitlich begrenzte Testversionen",
            "category": "trial"
        },
        "activity_logs": {
            "name": "Aktivitätslogs",
            "description": "Alle Useraktionen (DSGVO-Konformität)",
            "category": "compliance"
        },
        "email_notifications": {
            "name": "E-Mail-Benachrichtigungen",
            "description": "Bei wichtigen Ereignissen",
            "category": "notifications"
        },
        "custom_branding": {
            "name": "Custom Branding",
            "description": "Pro Team/Workspace (Farben, Logo, Impressum)",
            "category": "branding"
        },
        "mobile_first_optimization": {
            "name": "Mobile-First WebApp",
            "description": "Optimierung für mobile Geräte",
            "category": "ui"
        },
        
        # Premium Integrationen & Extra-Security
        "2fa_telegram_code": {
            "name": "2FA-Login per Telegram + Code",
            "description": "Zwei-Faktor-Authentifizierung",
            "category": "security"
        },
        "ip_whitelist_blacklist": {
            "name": "IP-Whitelist/Blacklist",
            "description": "Pro User konfigurierbar",
            "category": "security"
        },
        "api_access_logging": {
            "name": "Logging aller API-Zugriffe",
            "description": "Vollständige API-Audit-Logs",
            "category": "security"
        },
        "webhook_all_actions": {
            "name": "Webhook für alle Aktionen",
            "description": "Audit/Monitoring",
            "category": "monitoring"
        },
        "backup_settings": {
            "name": "Backup aller Settings",
            "description": "Pro User/Gruppe auf Knopfdruck",
            "category": "backup"
        },
        "export_import_config": {
            "name": "Export/Import der Konfiguration",
            "description": "JSON/YAML Format",
            "category": "backup"
        }
    }
    
    # 2. Paket-Templates erstellen
    package_templates = [
        {
            "name": "starter",
            "display_name": "Starter",
            "package_type": "starter",
            "monthly_price": 49.99,
            "one_time_price": None,
            "features": {
                # Nachrichten-Weiterleitung
                "message_forwarding_basic": True,
                "message_forwarding_pro": False,
                "message_forwarding_expert": False,
                
                # Gruppenverwaltung
                "group_management_basic": True,
                "group_management_pro": False,
                "group_management_expert": False,
                
                # Signalgruppen
                "signal_groups_basic": True,
                "signal_groups_pro": False,
                "signal_groups_expert": False,
                
                # Basis-Features
                "usdt_billing": True,
                "user_management": False,
                "mobile_first_optimization": True,
                
                # Alle Addons deaktiviert
                "time_scheduled_forwarding": False,
                "text_replacement_rules": False,
                "duplicate_filter": False,
                "webhook_triggered_messages": False,
                "message_statistics": False,
                "anonymous_forwarding": False,
                "auto_group_welcome": False,
                "invite_link_generator": False,
                "group_backup_restore": False,
                "user_limit_per_group": False,
                "auto_kick_bots_spam": False,
                "performance_tracking": False,
                "signal_notifications": False,
                "individual_notification_settings": False,
                "external_signal_api": False,
                "multi_language_support": False,
                "darkmode_webui": False,
                "lifetime_monthly_model": False,
                "auto_invoice_email": False,
                "bot_admin_panel": False,
                "api_webhooks": False,
                "media_forwarding": False,
                "advanced_filter_logic": False,
                "custom_package_upgrades": False,
                "free_trial_7_days": False,
                "activity_logs": False,
                "email_notifications": False,
                "custom_branding": False,
                "2fa_telegram_code": False,
                "ip_whitelist_blacklist": False,
                "api_access_logging": False,
                "webhook_all_actions": False,
                "backup_settings": False,
                "export_import_config": False
            }
        },
        {
            "name": "pro",
            "display_name": "Pro",
            "package_type": "pro",
            "monthly_price": 99.99,
            "one_time_price": None,
            "features": {
                # Nachrichten-Weiterleitung
                "message_forwarding_basic": True,
                "message_forwarding_pro": True,
                "message_forwarding_expert": False,
                
                # Gruppenverwaltung
                "group_management_basic": True,
                "group_management_pro": True,
                "group_management_expert": False,
                
                # Signalgruppen
                "signal_groups_basic": True,
                "signal_groups_pro": True,
                "signal_groups_expert": False,
                
                # Erweiterte Features
                "usdt_billing": True,
                "user_management": True,
                "mobile_first_optimization": True,
                "bot_admin_panel": True,
                "media_forwarding": True,
                "advanced_filter_logic": True,
                "activity_logs": True,
                "email_notifications": True,
                
                # Einige Addons aktiviert
                "time_scheduled_forwarding": True,
                "text_replacement_rules": True,
                "duplicate_filter": True,
                "auto_group_welcome": True,
                "invite_link_generator": True,
                "performance_tracking": True,
                "signal_notifications": True,
                "multi_language_support": True,
                "darkmode_webui": True,
                "lifetime_monthly_model": True,
                
                # Premium Features deaktiviert
                "message_forwarding_expert": False,
                "group_management_expert": False,
                "signal_groups_expert": False,
                "webhook_triggered_messages": False,
                "message_statistics": False,
                "anonymous_forwarding": False,
                "group_backup_restore": False,
                "user_limit_per_group": False,
                "auto_kick_bots_spam": False,
                "individual_notification_settings": False,
                "external_signal_api": False,
                "auto_invoice_email": False,
                "api_webhooks": False,
                "custom_package_upgrades": False,
                "free_trial_7_days": False,
                "custom_branding": False,
                "2fa_telegram_code": False,
                "ip_whitelist_blacklist": False,
                "api_access_logging": False,
                "webhook_all_actions": False,
                "backup_settings": False,
                "export_import_config": False
            }
        },
        {
            "name": "expert",
            "display_name": "Expert",
            "package_type": "expert",
            "monthly_price": 199.99,
            "one_time_price": None,
            "features": {
                # Alle Features aktiviert
                "message_forwarding_basic": True,
                "message_forwarding_pro": True,
                "message_forwarding_expert": True,
                "group_management_basic": True,
                "group_management_pro": True,
                "group_management_expert": True,
                "signal_groups_basic": True,
                "signal_groups_pro": True,
                "signal_groups_expert": True,
                "usdt_billing": True,
                "user_management": True,
                "mobile_first_optimization": True,
                "bot_admin_panel": True,
                "api_webhooks": True,
                "media_forwarding": True,
                "advanced_filter_logic": True,
                "activity_logs": True,
                "email_notifications": True,
                "time_scheduled_forwarding": True,
                "text_replacement_rules": True,
                "duplicate_filter": True,
                "webhook_triggered_messages": True,
                "message_statistics": True,
                "anonymous_forwarding": True,
                "auto_group_welcome": True,
                "invite_link_generator": True,
                "group_backup_restore": True,
                "user_limit_per_group": True,
                "auto_kick_bots_spam": True,
                "performance_tracking": True,
                "signal_notifications": True,
                "individual_notification_settings": True,
                "external_signal_api": True,
                "multi_language_support": True,
                "darkmode_webui": True,
                "lifetime_monthly_model": True,
                "auto_invoice_email": True,
                "custom_package_upgrades": True,
                "free_trial_7_days": True,
                "custom_branding": True,
                "2fa_telegram_code": True,
                "ip_whitelist_blacklist": True,
                "api_access_logging": True,
                "webhook_all_actions": True,
                "backup_settings": True,
                "export_import_config": True
            }
        },
        {
            "name": "lifetime",
            "display_name": "Lifetime",
            "package_type": "lifetime",
            "monthly_price": None,
            "one_time_price": 999.99,
            "features": {
                # Alle Features aktiviert (wie Expert)
                "message_forwarding_basic": True,
                "message_forwarding_pro": True,
                "message_forwarding_expert": True,
                "group_management_basic": True,
                "group_management_pro": True,
                "group_management_expert": True,
                "signal_groups_basic": True,
                "signal_groups_pro": True,
                "signal_groups_expert": True,
                "usdt_billing": True,
                "user_management": True,
                "mobile_first_optimization": True,
                "bot_admin_panel": True,
                "api_webhooks": True,
                "media_forwarding": True,
                "advanced_filter_logic": True,
                "activity_logs": True,
                "email_notifications": True,
                "time_scheduled_forwarding": True,
                "text_replacement_rules": True,
                "duplicate_filter": True,
                "webhook_triggered_messages": True,
                "message_statistics": True,
                "anonymous_forwarding": True,
                "auto_group_welcome": True,
                "invite_link_generator": True,
                "group_backup_restore": True,
                "user_limit_per_group": True,
                "auto_kick_bots_spam": True,
                "performance_tracking": True,
                "signal_notifications": True,
                "individual_notification_settings": True,
                "external_signal_api": True,
                "multi_language_support": True,
                "darkmode_webui": True,
                "lifetime_monthly_model": True,
                "auto_invoice_email": True,
                "custom_package_upgrades": True,
                "free_trial_7_days": True,
                "custom_branding": True,
                "2fa_telegram_code": True,
                "ip_whitelist_blacklist": True,
                "api_access_logging": True,
                "webhook_all_actions": True,
                "backup_settings": True,
                "export_import_config": True
            }
        }
    ]
    
    # 3. Package Templates in Datenbank einfügen
    for template in package_templates:
        cursor.execute("""
            INSERT INTO package_templates 
            (name, display_name, package_type, monthly_price, one_time_price, features, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            template["name"],
            template["display_name"],
            template["package_type"],
            template["monthly_price"],
            template["one_time_price"],
            json.dumps(template["features"]),
            True,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        print(f"✅ {template['display_name']} Template erstellt")
    
    # 4. Addons erstellen (für erweiterbare Features)
    addons = [
        {
            "name": "premium_security",
            "display_name": "Premium Security",
            "description": "2FA, IP-Whitelist, API-Logging",
            "monthly_price": 29.99,
            "one_time_price": None
        },
        {
            "name": "advanced_analytics",
            "display_name": "Advanced Analytics",
            "description": "Detaillierte Statistiken und Performance-Tracking",
            "monthly_price": 19.99,
            "one_time_price": None
        },
        {
            "name": "custom_branding",
            "display_name": "Custom Branding",
            "description": "Eigene Farben, Logo und Impressum",
            "monthly_price": 39.99,
            "one_time_price": None
        },
        {
            "name": "api_access",
            "display_name": "API Access",
            "description": "Vollständiger API-Zugriff mit Webhooks",
            "monthly_price": 49.99,
            "one_time_price": None
        },
        {
            "name": "backup_restore",
            "display_name": "Backup & Restore",
            "description": "Automatische Backups und Export/Import",
            "monthly_price": 15.99,
            "one_time_price": None
        }
    ]
    
    for addon in addons:
        cursor.execute("""
            INSERT INTO addons 
            (name, display_name, description, monthly_price, one_time_price, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            addon["name"],
            addon["display_name"],
            addon["description"],
            addon["monthly_price"],
            addon["one_time_price"],
            True,
            datetime.utcnow(),
            datetime.utcnow()
        ))
        print(f"✅ {addon['display_name']} Addon erstellt")
    
    conn.commit()
    conn.close()
    
    print("✅ Neue Paketstruktur erfolgreich erstellt!")
    print(f"📦 {len(package_templates)} Paket-Templates erstellt")
    print(f"🔧 {len(addons)} Addons erstellt")
    print(f"🎯 {len(feature_matrix)} Features definiert")

if __name__ == "__main__":
    setup_new_packages() 