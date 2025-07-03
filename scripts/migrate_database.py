#!/usr/bin/env python3
"""
Migration-Skript für die Datenbank
Migriert von der alten Struktur zur neuen Paket-System-Struktur
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import (
    User, Package, Payment, PackageTemplate, Addon, AddonTier, PackageAddon, UserAddon
)
import json
from datetime import datetime

# Datenbankverbindung
DATABASE_URL = "sqlite:///../telegram_bot.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def backup_existing_data():
    """Backup der bestehenden User-Daten"""
    print("💾 Erstelle Backup der bestehenden Daten...")
    
    db = SessionLocal()
    
    # Alle User-Daten sichern
    users = db.query(User).all()
    user_backup = []
    for user in users:
        user_data = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "phone": user.phone,
            "is_superadmin": user.is_superadmin,
            "is_active": user.is_active,
            "role": user.role,
            "login_code": user.login_code,
            "login_code_expires_at": user.login_code_expires_at.isoformat() if user.login_code_expires_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        user_backup.append(user_data)
    
    # Alle bestehenden Pakete sichern
    packages = db.query(Package).all()
    package_backup = []
    for package in packages:
        package_data = {
            "id": package.id,
            "name": package.name,
            "price": package.price,
            "duration_days": package.duration_days,
            "features": package.features,
            "user_id": package.user_id,
            "status": package.status,
            "start_date": package.start_date.isoformat() if package.start_date else None,
            "end_date": package.end_date.isoformat() if package.end_date else None,
            "created_at": package.created_at.isoformat() if package.created_at else None
        }
        package_backup.append(package_data)
    
    # Backup in JSON-Datei speichern
    backup_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "users": user_backup,
        "packages": package_backup
    }
    
    with open("database_backup.json", "w") as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"✅ Backup erstellt: {len(user_backup)} User, {len(package_backup)} Pakete")
    db.close()

def create_new_tables():
    """Erstellt alle neuen Tabellen"""
    print("🔧 Erstelle neue Tabellen...")
    Base.metadata.create_all(bind=engine)
    print("✅ Neue Tabellen erstellt")

def migrate_user_data():
    """Migriert User-Daten zur neuen Struktur"""
    print("👥 Migriere User-Daten...")
    
    db = SessionLocal()
    
    # Alle User aus der Backup-Datei wiederherstellen
    with open("database_backup.json", "r") as f:
        backup_data = json.load(f)
    
    # Bestehende User löschen (da sie möglicherweise inkonsistent sind)
    db.query(User).delete()
    db.commit()
    
    # User aus Backup wiederherstellen
    for user_data in backup_data["users"]:
        # Datetime-Felder korrekt verarbeiten
        login_code_expires_at = None
        if user_data["login_code_expires_at"]:
            try:
                login_code_expires_at = datetime.fromisoformat(user_data["login_code_expires_at"])
            except:
                pass
        
        created_at = None
        if user_data["created_at"]:
            try:
                created_at = datetime.fromisoformat(user_data["created_at"])
            except:
                created_at = datetime.utcnow()
        
        user = User(
            id=user_data["id"],
            telegram_id=user_data["telegram_id"],
            phone=user_data["phone"],
            is_superadmin=user_data["is_superadmin"],
            is_active=user_data["is_active"],
            role=user_data["role"],
            login_code=user_data["login_code"],
            login_code_expires_at=login_code_expires_at,
            created_at=created_at
        )
        db.add(user)
    
    db.commit()
    print(f"✅ {len(backup_data['users'])} User migriert")

def migrate_package_data():
    """Migriert Paket-Daten zur neuen Struktur"""
    print("📦 Migriere Paket-Daten...")
    
    db = SessionLocal()
    
    with open("database_backup.json", "r") as f:
        backup_data = json.load(f)
    
    # Bestehende Pakete löschen
    db.query(Package).delete()
    db.commit()
    
    # Pakete aus Backup wiederherstellen
    for package_data in backup_data["packages"]:
        # Datetime-Felder korrekt verarbeiten
        start_date = None
        if package_data["start_date"]:
            try:
                start_date = datetime.fromisoformat(package_data["start_date"])
            except:
                pass
        
        end_date = None
        if package_data["end_date"]:
            try:
                end_date = datetime.fromisoformat(package_data["end_date"])
            except:
                pass
        
        created_at = None
        if package_data["created_at"]:
            try:
                created_at = datetime.fromisoformat(package_data["created_at"])
            except:
                created_at = datetime.utcnow()
        
        # Features als JSON speichern
        features = package_data["features"]
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except:
                features = {}
        elif features is None:
            features = {}
        
        package = Package(
            id=package_data["id"],
            name=package_data["name"],
            price=package_data["price"],
            duration_days=package_data["duration_days"],
            features=features,
            user_id=package_data["user_id"],
            status=package_data["status"],
            start_date=start_date,
            end_date=end_date,
            created_at=created_at
        )
        db.add(package)
    
    db.commit()
    print(f"✅ {len(backup_data['packages'])} Pakete migriert")

def setup_default_package_templates():
    """Erstellt die Standard-Paket-Templates"""
    print("📋 Erstelle Standard-Paket-Templates...")
    
    db = SessionLocal()
    
    # Prüfen ob Templates bereits existieren
    existing_templates = db.query(PackageTemplate).count()
    if existing_templates > 0:
        print("⚠️ Paket-Templates existieren bereits, überspringe...")
        db.close()
        return
    
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
            "package_type": "basic",
            "monthly_price": 99.0,
            "one_time_price": None,
            "features": basic_features
        },
        {
            "name": "advanced",
            "display_name": "Advanced", 
            "package_type": "advanced",
            "monthly_price": 199.0,
            "one_time_price": None,
            "features": advanced_features
        },
        {
            "name": "pro",
            "display_name": "Pro",
            "package_type": "pro",
            "monthly_price": 299.0,
            "one_time_price": None,
            "features": pro_features
        },
        {
            "name": "lifetime",
            "display_name": "Lifetime",
            "package_type": "lifetime",
            "monthly_price": None,
            "one_time_price": 1999.0,
            "features": lifetime_features
        }
    ]
    
    for template_data in templates:
        template = PackageTemplate(**template_data)
        db.add(template)
        print(f"✅ {template_data['display_name']} Template erstellt")
    
    db.commit()
    db.close()

def main():
    """Hauptfunktion"""
    print("🚀 Datenbank-Migration startet...")
    print("=" * 50)
    
    try:
        # 1. Backup erstellen
        backup_existing_data()
        
        # 2. Neue Tabellen erstellen
        create_new_tables()
        
        # 3. User-Daten migrieren
        migrate_user_data()
        
        # 4. Paket-Daten migrieren
        migrate_package_data()
        
        # 5. Standard-Paket-Templates erstellen
        setup_default_package_templates()
        
        print("\n✅ Migration erfolgreich abgeschlossen!")
        print("\n📋 Was wurde gemacht:")
        print("- Backup der bestehenden Daten erstellt")
        print("- Neue Tabellen für Paket-System angelegt")
        print("- User-Daten migriert und beibehalten")
        print("- Paket-Daten migriert und beibehalten")
        print("- Standard-Paket-Templates erstellt")
        print("\n🎯 Das System ist jetzt bereit für das neue Paket-System!")
        
    except Exception as e:
        print(f"❌ Fehler bei der Migration: {e}")
        print("\n💡 Tipp: Prüfe die database_backup.json Datei für deine Daten")
        sys.exit(1)

if __name__ == "__main__":
    main() 