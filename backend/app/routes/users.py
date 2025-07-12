from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Payment, Package, UserbotSession, ForwardingGroupMapping
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import json
from typing import List, Optional
from ..schemas import UserbotSessionCreate, UserbotSessionUpdate, UserbotSessionResponse, SignalGroupResponse, SignalGroupSubscriptionResponse, SignalGroupSubscriptionCreate, SignalThemeResponse, SignalGroupThemeSubscriptionResponse, SignalGroupThemeSubscriptionCreate
from ..routes.auth import get_current_user
import httpx
import os

# Userbot API URL - aus zentraler .env-Datei
USERBOT_API_URL = os.getenv("USERBOT_URL", "http://localhost:8001")

router = APIRouter()
logger = logging.getLogger(__name__)

# -------------- Request-Modelle ---------------
class UserRegisterRequest(BaseModel):
    telegram_id: str                  # Pflichtfeld
    phone: str | None = None          # Optional, nur für Userbot

class UserUpdateRequest(BaseModel):
    telegram_id: str
    user_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    is_bot: bool | None = None
    language_code: str | None = None

# -------------- Helfer: Paid-Status ----------
def is_user_paid(user: User, db: Session):
    if not user.package_id:
        return False
    payment = (
        db.query(Payment)
        .filter(Payment.user_id == user.id, Payment.status == "bezahlt")
        .order_by(Payment.created_at.desc())
        .first()
    )
    if not payment:
        return False
    package = db.query(Package).filter(Package.id == payment.package_id).first()
    if not package:
        return False
    if package.duration_days == 0:
        return True
    ablaufdatum = payment.created_at + timedelta(days=int(package.duration_days))
    return datetime.utcnow() < ablaufdatum

# -------------- Paid-Status abfragen ----------
@router.get("/{telegram_id}/is_paid")
def check_paid_status(telegram_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        return {"paid": False}
    return {"paid": is_user_paid(user, db)}

# -------------- User registrieren/updaten -----
@router.post("/register_or_update")
def register_or_update_user(user_data: dict, db: Session = Depends(get_db)):
    """
    Registriert einen neuen User oder aktualisiert bestehenden User
    Wird vom Bot aufgerufen, wenn User /start sendet
    """
    try:
        # Validierung der Eingabedaten
        if not isinstance(user_data, dict):
            raise HTTPException(status_code=400, detail="Ungültiges Datenformat")
        
        telegram_id = user_data.get("telegram_id")
        if not telegram_id:
            raise HTTPException(status_code=400, detail="Telegram-ID erforderlich")
        
        # Prüfe ob User bereits existiert
        existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if existing_user:
            # User existiert - aktualisiere nur die Telegram-Daten
            logger.info(f"🔄 Aktualisiere bestehenden User {telegram_id}")
            
            # Aktualisiere nur Telegram-spezifische Felder
            existing_user.user_name = user_data.get("user_name", existing_user.user_name)
            existing_user.first_name = user_data.get("first_name", existing_user.first_name)
            existing_user.last_name = user_data.get("last_name", existing_user.last_name)
            existing_user.username = user_data.get("username", existing_user.username)
            existing_user.last_login = datetime.utcnow()
            
            db.commit()
            
            return {
                "success": True,
                "message": "User aktualisiert",
                "user_id": existing_user.id,
                "telegram_id": existing_user.telegram_id,
                "phone": existing_user.phone,
                "is_registered": existing_user.phone is not None
            }
        else:
            # Neuer User - erstelle mit Telegram-ID
            logger.info(f"🆕 Erstelle neuen User mit Telegram-ID {telegram_id}")
            
            new_user = User(
                telegram_id=telegram_id,
                user_name=user_data.get("user_name"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                username=user_data.get("username"),
                is_active=True,
                role="user",
                created_at=datetime.utcnow(),
                last_login=datetime.utcnow()
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            return {
                "success": True,
                "message": "User vorregistriert",
                "user_id": new_user.id,
                "telegram_id": new_user.telegram_id,
                "phone": None,
                "is_registered": False
            }
            
    except Exception as e:
        logger.error(f"❌ Fehler bei User-Registrierung: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Registrierung fehlgeschlagen: {str(e)}")

@router.post("/register_phone")
def register_phone_to_user(phone_data: dict, db: Session = Depends(get_db)):
    """
    Verknüpft eine Telefonnummer mit einer bestehenden Telegram-ID
    Wird vom Bot aufgerufen, wenn User Kontakt teilt
    """
    try:
        telegram_id = phone_data.get("telegram_id")
        phone = phone_data.get("phone")
        
        if not telegram_id or not phone:
            raise HTTPException(status_code=400, detail="Telegram-ID und Telefonnummer erforderlich")
        
        # Prüfe ob User mit dieser Telegram-ID existiert
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user is None:
            logger.error(f"❌ User mit Telegram-ID {telegram_id} nicht gefunden")
            raise HTTPException(status_code=404, detail="User mit dieser Telegram-ID nicht gefunden")
        
        # Prüfe ob Telefonnummer bereits vergeben ist
        existing_phone_user = db.query(User).filter(User.phone == phone).first()
        if existing_phone_user is not None and existing_phone_user.id != user.id:
            logger.error(f"❌ Telefonnummer {phone} bereits vergeben an User {existing_phone_user.id}")
            raise HTTPException(status_code=409, detail="Diese Telefonnummer ist bereits vergeben")
        
        # Verknüpfe Telefonnummer mit bestehendem User
        user.phone = phone
        user.last_login = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ Telefonnummer {phone} mit Telegram-ID {telegram_id} verknüpft")

        # --- Automatische Userbot-Session-Erstellung ---
        try:
            if user.package_id:
                from ..schemas import UserbotSessionCreate
                from ..models import UserbotSession
                # Prüfe, ob schon eine Session für diese Nummer existiert
                existing_session = db.query(UserbotSession).filter(
                    UserbotSession.user_id == user.id,
                    UserbotSession.phone == phone
                ).first()
                if not existing_session:
                    session_data = UserbotSessionCreate(
                        session_name="Auto-Session",
                        session_type="message_forwarding",
                        phone=phone,
                        is_active=True
                    )
                    new_session = UserbotSession(
                        user_id=user.id,
                        session_name=session_data.session_name,
                        session_type=session_data.session_type,
                        phone=session_data.phone,
                        is_active=True
                    )
                    db.add(new_session)
                    db.commit()
                    db.refresh(new_session)
                    logger.info(f"✅ Userbot-Session automatisch für User {user.id} und Nummer {phone} angelegt.")
        except Exception as session_error:
            logger.error(f"❌ Fehler beim automatischen Anlegen der Userbot-Session: {session_error}")
        
        return {
            "success": True,
            "message": "Telefonnummer erfolgreich verknüpft",
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "phone": user.phone,
            "is_registered": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Verknüpfen der Telefonnummer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Verknüpfung fehlgeschlagen: {str(e)}")

@router.post("/link_phone")
def link_phone_to_user(phone_data: dict, db: Session = Depends(get_db)):
    """
    Verknüpft eine Telefonnummer mit einer bestehenden Telegram-ID
    Wird vom WebUI aufgerufen, nachdem User seine Nummer eingegeben hat
    KEINE Authentifizierung erforderlich - wird vom Bot aufgerufen
    """
    try:
        logger.info(f"📞 Link Phone Request: {phone_data}")
        
        telegram_id = phone_data.get("telegram_id")
        phone = phone_data.get("phone")
        
        if not telegram_id or not phone:
            logger.error(f"❌ Fehlende Daten: telegram_id={telegram_id}, phone={phone}")
            raise HTTPException(status_code=400, detail="Telegram-ID und Telefonnummer erforderlich")
        
        # Prüfe ob User mit dieser Telegram-ID existiert
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user is None:
            logger.error(f"❌ User mit Telegram-ID {telegram_id} nicht gefunden")
            raise HTTPException(status_code=404, detail="User mit dieser Telegram-ID nicht gefunden")
        
        # Prüfe ob Telefonnummer bereits vergeben ist
        existing_phone_user = db.query(User).filter(User.phone == phone).first()
        if existing_phone_user is not None and existing_phone_user.id != user.id:
            logger.error(f"❌ Telefonnummer {phone} bereits vergeben an User {existing_phone_user.id}")
            raise HTTPException(status_code=409, detail="Diese Telefonnummer ist bereits vergeben")
        
        # Verknüpfe Telefonnummer
        user.phone = phone
        user.last_login = datetime.utcnow()
        
        try:
            db.commit()
            logger.info(f"✅ DB-Commit erfolgreich für User {user.id}")
        except Exception as commit_error:
            logger.error(f"❌ DB-Commit fehlgeschlagen: {commit_error}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Datenbankfehler beim Speichern")
        
        logger.info(f"✅ Telefonnummer {phone} mit Telegram-ID {telegram_id} verknüpft")

        # --- Automatische Userbot-Session-Erstellung ---
        try:
            if user.package_id:
                from ..schemas import UserbotSessionCreate
                from ..models import UserbotSession
                # Prüfe, ob schon eine Session für diese Nummer existiert
                existing_session = db.query(UserbotSession).filter(
                    UserbotSession.user_id == user.id,
                    UserbotSession.phone == phone
                ).first()
                if not existing_session:
                    session_data = UserbotSessionCreate(
                        session_name="Auto-Session",
                        session_type="message_forwarding",
                        phone=phone,
                        is_active=True
                    )
                    new_session = UserbotSession(
                        user_id=user.id,
                        session_name=session_data.session_name,
                        session_type=session_data.session_type,
                        phone=session_data.phone,
                        is_active=True
                    )
                    db.add(new_session)
                    db.commit()
                    db.refresh(new_session)
                    logger.info(f"✅ Userbot-Session automatisch für User {user.id} und Nummer {phone} angelegt.")
        except Exception as session_error:
            logger.error(f"❌ Fehler beim automatischen Anlegen der Userbot-Session: {session_error}")
        
        return {
            "success": True,
            "message": "Telefonnummer erfolgreich verknüpft",
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "phone": user.phone,
            "is_registered": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Verknüpfen der Telefonnummer: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Verknüpfung fehlgeschlagen: {str(e)}")

# Neue Route ohne Authentifizierung für Bot-Calls
@router.post("/link_phone_bot")
def link_phone_to_user_bot(phone_data: dict, db: Session = Depends(get_db)):
    """
    Verknüpft eine Telefonnummer mit einer bestehenden Telegram-ID
    Wird vom Bot aufgerufen - KEINE Authentifizierung erforderlich
    """
    try:
        logger.info(f"🤖 Bot Link Phone Request: {phone_data}")
        
        telegram_id = phone_data.get("telegram_id")
        phone = phone_data.get("phone")
        
        if not telegram_id or not phone:
            logger.error(f"❌ Fehlende Daten: telegram_id={telegram_id}, phone={phone}")
            raise HTTPException(status_code=400, detail="Telegram-ID und Telefonnummer erforderlich")
        
        # Prüfe ob User mit dieser Telegram-ID existiert
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if user is None:
            logger.error(f"❌ User mit Telegram-ID {telegram_id} nicht gefunden")
            raise HTTPException(status_code=404, detail="User mit dieser Telegram-ID nicht gefunden")
        
        # Prüfe ob Telefonnummer bereits vergeben ist
        existing_phone_user = db.query(User).filter(User.phone == phone).first()
        if existing_phone_user is not None and existing_phone_user.id != user.id:
            logger.error(f"❌ Telefonnummer {phone} bereits vergeben an User {existing_phone_user.id}")
            raise HTTPException(status_code=409, detail="Diese Telefonnummer ist bereits vergeben")
        
        # Verknüpfe Telefonnummer
        user.phone = phone
        user.last_login = datetime.utcnow()
        
        try:
            db.commit()
            logger.info(f"✅ DB-Commit erfolgreich für User {user.id}")
        except Exception as commit_error:
            logger.error(f"❌ DB-Commit fehlgeschlagen: {commit_error}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Datenbankfehler beim Speichern")
        
        logger.info(f"✅ Telefonnummer {phone} mit Telegram-ID {telegram_id} verknüpft (Bot)")

        # --- Automatische Userbot-Session-Erstellung ---
        try:
            if user.package_id:
                from ..schemas import UserbotSessionCreate
                from ..models import UserbotSession
                # Prüfe, ob schon eine Session für diese Nummer existiert
                existing_session = db.query(UserbotSession).filter(
                    UserbotSession.user_id == user.id,
                    UserbotSession.phone == phone
                ).first()
                if not existing_session:
                    session_data = UserbotSessionCreate(
                        session_name="Auto-Session",
                        session_type="message_forwarding",
                        phone=phone,
                        is_active=True
                    )
                    new_session = UserbotSession(
                        user_id=user.id,
                        session_name=session_data.session_name,
                        session_type=session_data.session_type,
                        phone=session_data.phone,
                        is_active=True
                    )
                    db.add(new_session)
                    db.commit()
                    db.refresh(new_session)
                    logger.info(f"✅ Userbot-Session automatisch für User {user.id} und Nummer {phone} angelegt.")
        except Exception as session_error:
            logger.error(f"❌ Fehler beim automatischen Anlegen der Userbot-Session: {session_error}")
        
        return {
            "success": True,
            "message": "Telefonnummer erfolgreich verknüpft",
            "user_id": user.id,
            "telegram_id": user.telegram_id,
            "phone": user.phone,
            "is_registered": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Verknüpfen der Telefonnummer (Bot): {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Verknüpfung fehlgeschlagen: {str(e)}")

# -------------- Userdetails nach Telegram-ID ----
@router.get("/by_telegram/{telegram_id}")
def get_user_by_telegram(telegram_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User nicht gefunden")
    return {
        "id": user.id,
        "telegram_id": user.telegram_id,
        "phone": user.phone,
        "is_partner": user.is_partner,
        "is_superadmin": user.is_superadmin,
        "package_id": user.package_id,
        "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")
    }

# -------------- Test-API für Datenintegrität ----
@router.get("/test/integrity")
def test_data_integrity(db: Session = Depends(get_db)):
    """Test-API: Gibt alle User und deren Telegram-IDs aus für Datenintegritätsprüfung"""
    try:
        users = db.query(User).all()
        user_data = []
        
        for user in users:
            user_data.append({
                "id": user.id,
                "telegram_id": user.telegram_id,
                "phone": user.phone,
                "user_name": user.user_name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "is_active": user.is_active,
                "role": user.role,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") if user.created_at else None,
                "last_login": user.last_login.strftime("%Y-%m-%d %H:%M:%S") if user.last_login else None,
                "package_id": user.package_id
            })
        
        return {
            "success": True,
            "total_users": len(user_data),
            "users": user_data,
            "database_path": str(db.bind.url) if hasattr(db.bind, 'url') else "unknown"
        }
        
    except Exception as e:
        logger.error(f"Fehler bei Datenintegritätsprüfung: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "total_users": 0,
            "users": []
        }

# ----------- USERBOT PACKAGE CHECK -----------

@router.get("/userbot-package-status")
async def check_userbot_package_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Prüft ob User ein aktives Userbot-Paket hat"""
    has_package = current_user.package_id is not None
    
    return {
        "has_userbot_package": has_package,
        "package_id": current_user.package_id,
        "message": "Userbot-Paket aktiv" if has_package else "Kein aktives Userbot-Paket gefunden"
        }

# ----------- USERBOT SESSIONS (ZENTRALISIERT) -----------
# Alle Userbot-Funktionalität wurde in /userbot/* Routen zentralisiert
# Siehe: backend/app/routes/userbot.py

# ----------- SIGNAL GROUPS FÜR USER -----------

@router.get("/signal-groups", response_model=List[SignalGroupResponse])
async def get_user_signal_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verfügbare Signalgruppen für den User abrufen"""
    # Nur aktive Signalgruppen anzeigen
    return db.query(SignalGroup).filter(SignalGroup.is_active == True).all()

@router.get("/signal-group-subscriptions", response_model=List[SignalGroupSubscriptionResponse])
async def get_user_signal_group_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Signalgruppen-Abonnements des Users abrufen"""
    return db.query(SignalGroupSubscription).filter(
        SignalGroupSubscription.user_id == current_user.id
    ).all()

@router.post("/signal-group-subscriptions", response_model=SignalGroupSubscriptionResponse)
async def create_signal_group_subscription(
    subscription_data: SignalGroupSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Neues Signalgruppen-Abonnement erstellen"""
    
    # Prüfe ob Signalgruppe existiert und aktiv ist
    signal_group = db.query(SignalGroup).filter(
        SignalGroup.id == subscription_data.signal_group_id,
        SignalGroup.is_active == True
    ).first()
    
    if not signal_group:
        raise HTTPException(status_code=404, detail="Signalgruppe nicht gefunden")
    
    # Prüfe ob User bereits ein aktives Abonnement hat
    existing_subscription = db.query(SignalGroupSubscription).filter(
        SignalGroupSubscription.user_id == current_user.id,
        SignalGroupSubscription.signal_group_id == subscription_data.signal_group_id,
        SignalGroupSubscription.status == "active"
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=400,
            detail="Sie haben bereits ein aktives Abonnement für diese Signalgruppe"
        )
    
    new_subscription = SignalGroupSubscription(
        user_id=current_user.id,
        signal_group_id=subscription_data.signal_group_id,
        group_count=subscription_data.group_count,
        status="active",
        start_date=datetime.utcnow()
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

# ----------- THEMATISCHE GRUPPEN-ABONNEMENTS -----------

@router.get("/signal-themes", response_model=List[SignalThemeResponse])
async def get_user_signal_themes(
    signal_group_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verfügbare thematische Gruppen für den User abrufen"""
    query = db.query(SignalTheme).filter(SignalTheme.is_active == True)
    
    if signal_group_id:
        query = query.filter(SignalTheme.signal_group_id == signal_group_id)
    
    return query.all()

@router.get("/signal-theme-subscriptions", response_model=List[SignalGroupThemeSubscriptionResponse])
async def get_user_theme_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thematische Gruppen-Abonnements des Users abrufen"""
    return db.query(SignalGroupThemeSubscription).filter(
        SignalGroupThemeSubscription.user_id == current_user.id
    ).all()

@router.post("/signal-theme-subscriptions", response_model=SignalGroupThemeSubscriptionResponse)
async def create_theme_subscription(
    subscription_data: SignalGroupThemeSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Neues thematisches Gruppen-Abonnement erstellen"""
    
    # Prüfe ob Thema existiert und aktiv ist
    theme = db.query(SignalTheme).filter(
        SignalTheme.id == subscription_data.theme_id,
        SignalTheme.is_active == True
    ).first()
    
    if not theme:
        raise HTTPException(status_code=404, detail="Thema nicht gefunden")
    
    # Prüfe ob User bereits ein aktives Abonnement für dieses Thema hat
    existing_subscription = db.query(SignalGroupThemeSubscription).filter(
        SignalGroupThemeSubscription.user_id == current_user.id,
        SignalGroupThemeSubscription.theme_id == subscription_data.theme_id,
        SignalGroupThemeSubscription.status == "active"
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=400,
            detail="Sie haben bereits ein aktives Abonnement für dieses Thema"
        )
    
    new_subscription = SignalGroupThemeSubscription(
        user_id=current_user.id,
        signal_group_id=subscription_data.signal_group_id,
        theme_id=subscription_data.theme_id,
        status="active",
        start_date=datetime.utcnow(),
        monthly_price=theme.price_monthly
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

@router.put("/signal-theme-subscriptions/{subscription_id}/cancel")
async def cancel_theme_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Thematisches Gruppen-Abonnement kündigen"""
    subscription = db.query(SignalGroupThemeSubscription).filter(
        SignalGroupThemeSubscription.id == subscription_id,
        SignalGroupThemeSubscription.user_id == current_user.id
    ).first()
    
    if subscription is None:
        raise HTTPException(status_code=404, detail="Abonnement nicht gefunden")
    
    subscription.status = "cancelled"
    subscription.end_date = datetime.utcnow()
    db.commit()
    
    return {"message": "Abonnement erfolgreich gekündigt"}

@router.get("/signal-groups/{signal_group_id}/themes-with-prices")
async def get_signal_group_themes_with_prices(
    signal_group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Themen einer Signal-Gruppe mit Preisen und User-Abonnement-Status abrufen"""
    
    # Hole alle aktiven Themen der Signal-Gruppe
    themes = db.query(SignalTheme).filter(
        SignalTheme.signal_group_id == signal_group_id,
        SignalTheme.is_active == True
    ).all()
    
    # Hole User-Abonnements für diese Themen
    user_subscriptions = db.query(SignalGroupThemeSubscription).filter(
        SignalGroupThemeSubscription.user_id == current_user.id,
        SignalGroupThemeSubscription.theme_id.in_([theme.id for theme in themes])
    ).all()
    
    # Erstelle Mapping für schnellen Zugriff
    subscription_map = {sub.theme_id: sub for sub in user_subscriptions}
    
    # Erstelle erweiterte Themen-Liste
    themes_with_status = []
    for theme in themes:
        user_subscription = subscription_map.get(theme.id)
        themes_with_status.append({
            "id": theme.id,
            "name": theme.name,
            "description": theme.description,
            "price_monthly": theme.price_monthly,
            "is_subscribed": user_subscription is not None and user_subscription.status == "active",
            "subscription_status": user_subscription.status if user_subscription else None,
            "subscription_end_date": user_subscription.end_date if user_subscription else None
        })
    
    return themes_with_status

# Hilfsfunktion für Standard-Konfigurationen
def get_default_config_for_session_type(session_type: str) -> dict:
    """Gibt Standard-Konfiguration für verschiedene Session-Typen zurück"""
    configs = {
        "message_forwarding": {
            "source_groups": [],
            "target_groups": [],
            "forward_all_messages": True,
            "forward_media": True,
            "forward_links": True,
            "filter_keywords": [],
            "exclude_keywords": [],
            "delay_seconds": 0
        },
        "signal_groups": {
            "signal_group_id": None,
            "auto_create_groups": True,
            "group_prefix": "Signal",
            "max_members_per_group": 1000,
            "forward_delay_seconds": 0,
            "filter_keywords": [],
            "exclude_keywords": []
        },
        "auto_reply": {
            "trigger_keywords": [],
            "reply_messages": {},
            "reply_delay_seconds": 0,
            "max_replies_per_hour": 10
        },
        "custom": {
            "custom_script": "",
            "parameters": {}
        }
    }
    
    return configs.get(session_type, {})

# --- Nachrichtenweiterleitung per Userbot ---

@router.get("/userbot/groups")
async def get_userbot_groups(
    current_user: User = Depends(get_current_user)
):
    """Holt alle verfügbaren Gruppen für den Userbot."""
    try:
        # Prüfe Berechtigung
        if not (current_user.is_superadmin or 
                current_user.role == 'partner' or 
                current_user.package_id):
            raise HTTPException(status_code=403, detail="Keine Berechtigung für Userbot-Services")
        
        # Userbot-Service aufrufen
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{USERBOT_API_URL}/api/dialogs")
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "groups": data.get("dialogs", [])
                    }
                else:
                    logger.error(f"Userbot-Service Fehler: {response.status_code} - {response.text}")
                    raise HTTPException(status_code=400, detail="Fehler beim Laden der Gruppen")
                    
            except httpx.ConnectError:
                logger.error(f"Userbot-Service nicht erreichbar: {USERBOT_API_URL}")
                raise HTTPException(status_code=503, detail="Userbot-Service nicht erreichbar")
            except httpx.TimeoutException:
                logger.error("Userbot-Service Timeout")
                raise HTTPException(status_code=504, detail="Userbot-Service Timeout")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Laden der Userbot-Gruppen: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Gruppen: {str(e)}")

@router.post("/userbot/forwarding/activate")
async def activate_userbot_forwarding(
    source_group_id: str = Body(...),
    target_group_id: str = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktiviert die Nachrichtenweiterleitung für den eingeloggten User."""
    try:
        # Prüfe Berechtigung
        if not (current_user.is_superadmin or 
                current_user.role == 'partner' or 
                current_user.package_id):
            raise HTTPException(status_code=403, detail="Keine Berechtigung für Userbot-Services")
        
        session = db.query(UserbotSession).filter(
            UserbotSession.user_id == current_user.id,
            UserbotSession.session_type == "message_forwarding"
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Keine Userbot-Session gefunden. Bitte melden Sie sich zuerst an.")
        
        # Mapping anlegen (oder reaktivieren)
        mapping = db.query(ForwardingGroupMapping).filter(
            ForwardingGroupMapping.userbot_session_id == session.id,
            ForwardingGroupMapping.source_group_id == source_group_id,
            ForwardingGroupMapping.target_group_id == target_group_id
        ).first()
        
        if mapping:
            mapping.forwarding_active = True
            db.commit()
        else:
            mapping = ForwardingGroupMapping(
                userbot_session_id=session.id,
                source_group_id=source_group_id,
                target_group_id=target_group_id,
                forwarding_active=True
            )
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
        
        return {"success": True, "session_id": session.id, "mapping_id": mapping.id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Aktivieren der Weiterleitung: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktivieren der Weiterleitung: {str(e)}")

@router.get("/userbot/forwarding/status")
async def get_userbot_forwarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt Status, registrierte Gruppen und Sessionstatus zurück."""
    try:
        session = db.query(UserbotSession).filter(
            UserbotSession.user_id == current_user.id,
            UserbotSession.session_type == "message_forwarding"
        ).first()
        
        if not session:
            return {"active": False, "forwarding_enabled": False, "groups": [], "session": None}
        
        mappings = db.query(ForwardingGroupMapping).filter(
            ForwardingGroupMapping.userbot_session_id == session.id
        ).all()
        
        group_pairs = [
            {
                "id": mapping.id,
                "source_group_id": mapping.source_group_id,
                "target_group_id": mapping.target_group_id,
                "forwarding_active": mapping.forwarding_active,
                "created_at": mapping.created_at.isoformat()
            } for mapping in mappings
        ]
        
        return {
            "active": session.is_active and session.forwarding_enabled,
            "forwarding_enabled": session.forwarding_enabled,
            "groups": group_pairs,
            "session": {
                "id": session.id,
                "session_name": session.session_name,
                "session_type": session.session_type,
                "is_active": session.is_active,
                "forwarding_enabled": session.forwarding_enabled
            }
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Weiterleitungsstatus: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Status: {str(e)}")

@router.patch("/userbot/forwarding-mapping/{mapping_id}/toggle")
async def toggle_userbot_forwarding_mapping(
    mapping_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktiviert/Deaktiviert eine Weiterleitungs-Mapping"""
    try:
        # Prüfe ob Mapping existiert und dem User gehört
        mapping = db.query(ForwardingGroupMapping).join(UserbotSession).filter(
            ForwardingGroupMapping.id == mapping_id,
            UserbotSession.user_id == current_user.id
        ).first()
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping nicht gefunden")
        
        mapping.forwarding_active = not mapping.forwarding_active
        db.commit()
        db.refresh(mapping)
        
        return {
            "success": True,
            "message": f"Weiterleitung {'aktiviert' if mapping.forwarding_active else 'deaktiviert'}",
            "forwarding_active": mapping.forwarding_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler beim Umschalten des Mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Umschalten des Mappings: {str(e)}")

@router.delete("/userbot/forwarding-mapping/{mapping_id}")
async def delete_userbot_forwarding_mapping(
    mapping_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Löscht eine Weiterleitungs-Mapping"""
    try:
        # Prüfe ob Mapping existiert und dem User gehört
        mapping = db.query(ForwardingGroupMapping).join(UserbotSession).filter(
            ForwardingGroupMapping.id == mapping_id,
            UserbotSession.user_id == current_user.id
        ).first()
        
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping nicht gefunden")
        
        db.delete(mapping)
        db.commit()
        
        return {
            "success": True,
            "message": "Weiterleitungs-Mapping erfolgreich gelöscht"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Fehler beim Löschen des Mappings: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen des Mappings: {str(e)}")

# -------------- User Profile Endpoints ----------
@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt das Profil des aktuellen Users zurück"""
    try:
        return {
            "id": current_user.id,
            "telegram_id": current_user.telegram_id,
            "user_name": current_user.user_name,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "phone": current_user.phone,
            "username": current_user.username,
            "is_active": current_user.is_active,
            "role": current_user.role,
            "is_superadmin": current_user.is_superadmin,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen des User-Profils: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen des Profils: {str(e)}")

@router.put("/profile")
async def update_user_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualisiert das Profil des aktuellen Users"""
    try:
        # Erlaubte Felder zum Aktualisieren
        allowed_fields = ["user_name", "first_name", "last_name", "phone"]
        
        for field in allowed_fields:
            if field in profile_data:
                setattr(current_user, field, profile_data[field])
        
        current_user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        return {
            "success": True,
            "message": "Profil erfolgreich aktualisiert",
            "user": {
                "id": current_user.id,
                "telegram_id": current_user.telegram_id,
                "user_name": current_user.user_name,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone": current_user.phone
            }
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Aktualisieren des User-Profils: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren des Profils: {str(e)}")

# -------------- User Settings Endpoints ----------
@router.get("/settings")
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt die Einstellungen des Users zurück"""
    try:
        # Hier könnten User-spezifische Einstellungen aus der DB geladen werden
        # Für jetzt geben wir Standard-Einstellungen zurück
        return {
            "notifications": {
                "signal_notifications": True,
                "payment_notifications": True,
                "system_notifications": True
            },
            "security": {
                "two_factor_enabled": False,
                "session_timeout": True
            },
            "preferences": {
                "language": "de",
                "timezone": "Europe/Berlin"
            }
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der User-Einstellungen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Einstellungen: {str(e)}")

@router.put("/settings/notifications")
async def update_notification_settings(
    notification_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualisiert die Benachrichtigungseinstellungen"""
    try:
        # Hier würden die Einstellungen in der DB gespeichert werden
        return {
            "success": True,
            "message": "Benachrichtigungseinstellungen aktualisiert",
            "notifications": notification_data
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Aktualisieren der Benachrichtigungseinstellungen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Einstellungen: {str(e)}")

@router.put("/settings/security")
async def update_security_settings(
    security_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aktualisiert die Sicherheitseinstellungen"""
    try:
        # Hier würden die Einstellungen in der DB gespeichert werden
        return {
            "success": True,
            "message": "Sicherheitseinstellungen aktualisiert",
            "security": security_data
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Aktualisieren der Sicherheitseinstellungen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Einstellungen: {str(e)}")

# -------------- User Groups Endpoints ----------
@router.get("/groups")
async def get_user_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt alle Gruppen des Users zurück"""
    try:
        # Hier würden die Gruppen des Users aus der DB geladen werden
        # Für jetzt geben wir Mock-Daten zurück
        groups = [
            {
                "id": 1,
                "name": "Trading Gruppe 1",
                "status": "active",
                "member_count": 150,
                "signal_count": 25
            },
            {
                "id": 2,
                "name": "Trading Gruppe 2",
                "status": "active",
                "member_count": 89,
                "signal_count": 12
            }
        ]
        
        return groups
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der User-Gruppen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Gruppen: {str(e)}")

@router.post("/groups/{group_id}/join")
async def join_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Tritt einer Gruppe bei"""
    try:
        # Hier würde die Logik zum Beitreten einer Gruppe implementiert werden
        return {
            "success": True,
            "message": f"Erfolgreich Gruppe {group_id} beigetreten"
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Beitreten der Gruppe: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Beitreten der Gruppe: {str(e)}")

# -------------- Account Management ----------
@router.get("/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Exportiert alle Daten des Users"""
    try:
        # Sammle alle User-Daten
        user_data = {
            "profile": {
                "id": current_user.id,
                "telegram_id": current_user.telegram_id,
                "user_name": current_user.user_name,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "phone": current_user.phone,
                "username": current_user.username,
                "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            },
            "payments": [],
            "sessions": [],
            "groups": []
        }
        
        # Hole Zahlungen
        payments = db.query(Payment).filter(Payment.user_id == current_user.id).all()
        for payment in payments:
            user_data["payments"].append({
                "id": payment.id,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at.isoformat() if payment.created_at else None
            })
        
        # Hole Userbot-Sessions
        sessions = db.query(UserbotSession).filter(UserbotSession.user_id == current_user.id).all()
        for session in sessions:
            user_data["sessions"].append({
                "id": session.id,
                "phone": session.phone,
                "status": session.status,
                "created_at": session.created_at.isoformat() if session.created_at else None
            })
        
        return user_data
    except Exception as e:
        logger.error(f"❌ Fehler beim Exportieren der User-Daten: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Exportieren der Daten: {str(e)}")

@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Löscht das User-Konto"""
    try:
        # Hier würde die Logik zum sicheren Löschen des Kontos implementiert werden
        # Für jetzt markieren wir es nur als inaktiv
        current_user.is_active = False
        db.commit()
        
        return {
            "success": True,
            "message": "Konto erfolgreich gelöscht"
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Löschen des User-Kontos: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen des Kontos: {str(e)}")
