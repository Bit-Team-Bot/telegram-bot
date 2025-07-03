#!/usr/bin/env python3
"""
Setup-Skript für das neue Paket-System
Erstellt die neuen Tabellen und fügt Standarddaten ein
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import (
    PackageTemplate, Addon, AddonTier, PackageAddon,
    PackageType, AddonStatus
)
import json

# Datenbankverbindung
DATABASE_URL = "sqlite:///../telegram_bot.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Erstellt alle neuen Tabellen"""
    print("🔧 Erstelle neue Tabellen...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabellen erstellt")

def setup_package_templates():
    """Erstellt die Standard-Paket-Templates"""
    print("📦 Erstelle Paket-Templates...")
    
    db = SessionLocal()
    
    # Standard-Feature-Matrix
    basic_features = {
        "gruppen_weiterleitung": 1,
        "telegram_bot_integration": True,
        "webui_dashboard": True,
        "user_management": True,
        "payment_system": True,
        "session_management": True,
        "jwt_authentication": True,
        "telegram_login": True,
        "userbot_service": True,
        "sprachen_uebersetzung": False,
        "webhook_api": False,
        "wallet_management": False,
        "signalgruppen": False,
        "monitoring_analytics": False,
        "real_time_notifications": False,
        "group_management": False,
        "payment_history": False,
        "package_upgrades": False,
        "admin_panel": False,
        "rate_limiting": False,
        "security_headers": False,
        "cors_protection": False,
        "input_validation": False,
        "sql_injection_protection": False,
        "xss_protection": False,
        "csrf_protection": False,
        "backup_system": False,
        "ssl_https": False,
        "firewall_protection": False,
        "performance_optimization": False,
        "lazy_loading": False,
        "compression": False,
        "caching": False,
        "connection_pooling": False,
        "async_operations": False,
        "logging_monitoring": False,
        "health_checks": False,
        "error_handling": False,
        "internationalization": False,
        "responsive_design": False,
        "state_management": False,
        "api_documentation": False,
        "testing_framework": False,
        "deployment_automation": False,
        "docker_support": False,
        "systemd_services": False,
        "nginx_reverse_proxy": False,
        "cloudflare_integration": False
    }
    
    advanced_features = basic_features.copy()
    advanced_features.update({
        "gruppen_weiterleitung": 3,
        "monitoring_analytics": True,
        "real_time_notifications": True,
        "group_management": True,
        "payment_history": True,
        "package_upgrades": True,
        "rate_limiting": True,
        "security_headers": True,
        "cors_protection": True,
        "input_validation": True,
        "sql_injection_protection": True,
        "xss_protection": True,
        "csrf_protection": True,
        "performance_optimization": True,
        "lazy_loading": True,
        "compression": True,
        "caching": True,
        "connection_pooling": True,
        "async_operations": True,
        "logging_monitoring": True,
        "health_checks": True,
        "error_handling": True,
        "internationalization": True,
        "responsive_design": True,
        "state_management": True,
        "api_documentation": True
    })
    
    pro_features = advanced_features.copy()
    pro_features.update({
        "gruppen_weiterleitung": 5,
        "admin_panel": True,
        "backup_system": True,
        "ssl_https": True,
        "firewall_protection": True,
        "testing_framework": True,
        "deployment_automation": True,
        "docker_support": True,
        "systemd_services": True,
        "nginx_reverse_proxy": True,
        "cloudflare_integration": True
    })
    
    lifetime_features = pro_features.copy()
    lifetime_features.update({
        "gruppen_weiterleitung": "unbegrenzt",
        "sprachen_uebersetzung": True,
        "webhook_api": True,
        "wallet_management": True,
        "signalgruppen": True
    })
    
    # Paket-Templates erstellen
    templates = [
        {
            "name": "basic",
            "display_name": "Basic",
            "package_type": PackageType.BASIC.value,
            "monthly_price": 99.0,
            "one_time_price": None,
            "features": basic_features
        },
        {
            "name": "advanced",
            "display_name": "Advanced", 
            "package_type": PackageType.ADVANCED.value,
            "monthly_price": 199.0,
            "one_time_price": None,
            "features": advanced_features
        },
        {
            "name": "pro",
            "display_name": "Pro",
            "package_type": PackageType.PRO.value,
            "monthly_price": 299.0,
            "one_time_price": None,
            "features": pro_features
        },
        {
            "name": "lifetime",
            "display_name": "Lifetime",
            "package_type": PackageType.LIFETIME.value,
            "monthly_price": None,
            "one_time_price": 1999.0,
            "features": lifetime_features
        }
    ]
    
    for template_data in templates:
        existing = db.query(PackageTemplate).filter(PackageTemplate.name == template_data["name"]).first()
        if not existing:
            template = PackageTemplate(**template_data)
            db.add(template)
            print(f"✅ {template_data['display_name']} Template erstellt")
        else:
            print(f"⚠️ {template_data['display_name']} Template existiert bereits")
    
    db.commit()
    db.close()

def setup_addons():
    """Erstellt die Standard-Add-ons"""
    print("🔧 Erstelle Add-ons...")
    
    db = SessionLocal()
    
    addons_data = [
        {
            "name": "signalgruppen",
            "display_name": "Signalgruppen",
            "description": "Premium-Zugang zu exklusiven Signalgruppen",
            "monthly_price": 99.0,
            "one_time_price": None,
            "tiers": [
                {"level": "1", "price": 99.0, "description": "Signalgruppe Level 1"},
                {"level": "2", "price": 199.0, "description": "Signalgruppe Level 2"},
                {"level": "3", "price": 299.0, "description": "Signalgruppe Level 3"},
                {"level": "VIP", "price": 399.0, "description": "VIP Signalgruppe"}
            ]
        },
        {
            "name": "sprachen_uebersetzung",
            "display_name": "Sprachübersetzung",
            "description": "Automatische Übersetzung der Weiterleitungen",
            "monthly_price": 10.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "webhook_api",
            "display_name": "Webhook/API",
            "description": "API-Anbindung für eigene Integrationen",
            "monthly_price": 15.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "wallet_management",
            "display_name": "Wallet Management",
            "description": "Erweiterte Wallet-Funktionen und Management",
            "monthly_price": 20.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "monitoring_analytics",
            "display_name": "Monitoring & Analytics",
            "description": "Erweiterte Monitoring- und Analytics-Features",
            "monthly_price": 25.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "real_time_notifications",
            "display_name": "Real-time Notifications",
            "description": "Echtzeit-Benachrichtigungen und Alerts",
            "monthly_price": 15.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "admin_panel",
            "display_name": "Admin Panel",
            "description": "Vollständiges Admin-Panel mit erweiterten Funktionen",
            "monthly_price": 50.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "backup_system",
            "display_name": "Backup System",
            "description": "Automatische Backups und Wiederherstellung",
            "monthly_price": 10.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "ssl_https",
            "display_name": "SSL/HTTPS",
            "description": "SSL-Zertifikate und HTTPS-Verschlüsselung",
            "monthly_price": 5.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "firewall_protection",
            "display_name": "Firewall Protection",
            "description": "Erweiterte Firewall-Schutzfunktionen",
            "monthly_price": 15.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "performance_optimization",
            "display_name": "Performance Optimization",
            "description": "Performance-Optimierungen und Caching",
            "monthly_price": 20.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "testing_framework",
            "display_name": "Testing Framework",
            "description": "Vollständiges Testing-Framework",
            "monthly_price": 30.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "deployment_automation",
            "display_name": "Deployment Automation",
            "description": "Automatisierte Deployment-Prozesse",
            "monthly_price": 25.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "docker_support",
            "display_name": "Docker Support",
            "description": "Docker-Containerisierung und Orchestrierung",
            "monthly_price": 20.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "systemd_services",
            "display_name": "Systemd Services",
            "description": "Systemd-Service-Integration",
            "monthly_price": 10.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "nginx_reverse_proxy",
            "display_name": "Nginx Reverse Proxy",
            "description": "Nginx Reverse-Proxy-Konfiguration",
            "monthly_price": 15.0,
            "one_time_price": None,
            "tiers": []
        },
        {
            "name": "cloudflare_integration",
            "display_name": "Cloudflare Integration",
            "description": "Cloudflare-Integration und CDN",
            "monthly_price": 10.0,
            "one_time_price": None,
            "tiers": []
        }
    ]
    
    for addon_data in addons_data:
        tiers = addon_data.pop("tiers")
        
        existing = db.query(Addon).filter(Addon.name == addon_data["name"]).first()
        if not existing:
            addon = Addon(**addon_data)
            db.add(addon)
            db.flush()  # Um die ID zu bekommen
            
            # Tiers erstellen
            for tier_data in tiers:
                tier = AddonTier(addon_id=addon.id, **tier_data)
                db.add(tier)
            
            print(f"✅ {addon_data['display_name']} Add-on erstellt")
        else:
            print(f"⚠️ {addon_data['display_name']} Add-on existiert bereits")
    
    db.commit()
    db.close()

def setup_package_addons():
    """Verknüpft Pakete mit Add-ons"""
    print("🔗 Verknüpfe Pakete mit Add-ons...")
    
    db = SessionLocal()
    
    # Hole alle Templates und Add-ons
    templates = db.query(PackageTemplate).all()
    addons = db.query(Addon).all()
    
    # Standard-Konfiguration: Welche Add-ons für welche Pakete verfügbar sind
    package_addon_config = {
        "basic": ["sprachen_uebersetzung", "webhook_api", "wallet_management"],
        "advanced": ["sprachen_uebersetzung", "webhook_api", "wallet_management", 
                    "monitoring_analytics", "real_time_notifications", "backup_system"],
        "pro": ["sprachen_uebersetzung", "webhook_api", "wallet_management", 
               "monitoring_analytics", "real_time_notifications", "backup_system",
               "ssl_https", "firewall_protection", "performance_optimization",
               "testing_framework", "deployment_automation", "docker_support",
               "systemd_services", "nginx_reverse_proxy", "cloudflare_integration"],
        "lifetime": ["signalgruppen", "sprachen_uebersetzung", "webhook_api", 
                    "wallet_management", "monitoring_analytics", "real_time_notifications",
                    "admin_panel", "backup_system", "ssl_https", "firewall_protection",
                    "performance_optimization", "testing_framework", "deployment_automation",
                    "docker_support", "systemd_services", "nginx_reverse_proxy", 
                    "cloudflare_integration"]
    }
    
    for template in templates:
        if template.name in package_addon_config:
            for addon_name in package_addon_config[template.name]:
                addon = next((a for a in addons if a.name == addon_name), None)
                if addon:
                    existing = db.query(PackageAddon).filter(
                        PackageAddon.package_template_id == template.id,
                        PackageAddon.addon_id == addon.id
                    ).first()
                    
                    if not existing:
                        package_addon = PackageAddon(
                            package_template_id=template.id,
                            addon_id=addon.id,
                            is_enabled=True
                        )
                        db.add(package_addon)
                        print(f"✅ {template.display_name} ↔ {addon.display_name}")
    
    db.commit()
    db.close()

def main():
    """Hauptfunktion"""
    print("🚀 Setup für neues Paket-System")
    print("=" * 50)
    
    try:
        create_tables()
        setup_package_templates()
        setup_addons()
        setup_package_addons()
        
        print("\n✅ Paket-System Setup abgeschlossen!")
        print("\n📋 Erstellte Komponenten:")
        print("- Package Templates (Basic, Advanced, Pro, Lifetime)")
        print("- Add-ons mit Tiers (Signalgruppen, etc.)")
        print("- Package-Addon Verknüpfungen")
        print("\n🎯 Das System ist bereit für die Feature-Matrix!")
        
    except Exception as e:
        print(f"❌ Fehler beim Setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 