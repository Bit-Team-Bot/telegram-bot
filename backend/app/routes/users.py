from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from app.models import User, Package, Payment, UserRole, UserbotSession, SignalGroup, SignalGroupSubscription, SignalTheme, SignalGroupThemeSubscription
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import json
from typing import List, Optional
from ..schemas import UserbotSessionCreate, UserbotSessionUpdate, UserbotSessionResponse, SignalGroupResponse, SignalGroupSubscriptionResponse, SignalGroupSubscriptionCreate, SignalThemeResponse, SignalGroupThemeSubscriptionResponse, SignalGroupThemeSubscriptionCreate
from ..routes.auth import get_current_user

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

# ----------- USERBOT SESSIONS -----------

@router.get("/userbot-sessions", response_model=List[UserbotSessionResponse])
async def get_userbot_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Userbot-Sessions des aktuellen Users abrufen"""
    
    # Prüfe ob User ein aktives Userbot-Paket hat
    if not current_user.package_id:
        raise HTTPException(
            status_code=403,
            detail="Sie benötigen ein aktives Userbot-Paket, um Sessions zu verwalten. Bitte buchen Sie zuerst ein Paket."
        )
    
    return db.query(UserbotSession).filter(UserbotSession.user_id == current_user.id).all()

@router.post("/userbot-sessions", response_model=UserbotSessionResponse)
async def create_userbot_session(
    session_data: UserbotSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Neue Userbot-Session erstellen"""
    
    # Prüfe ob User ein aktives Userbot-Paket hat
    if not current_user.package_id:
        raise HTTPException(
            status_code=403,
            detail="Sie benötigen ein aktives Userbot-Paket, um eine Session zu erstellen. Bitte buchen Sie zuerst ein Paket."
        )
    
    # Prüfe ob bereits eine Session mit dieser Handynummer existiert
    existing_session = db.query(UserbotSession).filter(
        UserbotSession.user_id == current_user.id,
        UserbotSession.phone == session_data.phone
    ).first()
    
    if existing_session:
        raise HTTPException(
            status_code=400,
            detail="Es existiert bereits eine Session mit dieser Handynummer"
        )
    
    # Erstelle Standard-Konfiguration je nach Session-Typ
    config_data = get_default_config_for_session_type(session_data.session_type)
    
    # Berechne Abonnement-Daten
    now = datetime.utcnow()
    subscription_start = now
    subscription_end = now + timedelta(days=30)  # Standard: 30 Tage
    next_payment = subscription_end
    auto_delete = now + timedelta(weeks=2)  # 2 Wochen nach Erstellung
    
    new_session = UserbotSession(
        user_id=current_user.id,
        session_name=session_data.session_name,
        session_type=session_data.session_type,
        phone=session_data.phone,
        telegram_session_string=session_data.telegram_session_string,
        is_active=session_data.is_active,
        config_data=json.dumps(config_data) if config_data else None,
        subscription_status="active",
        subscription_start_date=subscription_start,
        subscription_end_date=subscription_end,
        next_payment_date=next_payment,
        auto_delete_date=auto_delete
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.put("/userbot-sessions/{session_id}", response_model=UserbotSessionResponse)
async def update_userbot_session(
    session_id: int,
    session_data: UserbotSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Userbot-Session bearbeiten"""
    session = db.query(UserbotSession).filter(
        UserbotSession.id == session_id,
        UserbotSession.user_id == current_user.id
    ).first()
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    # Aktualisiere Felder
    if session_data.session_name is not None:
        session.session_name = session_data.session_name
    if session_data.phone is not None:
        session.phone = session_data.phone
    if session_data.telegram_session_string is not None:
        session.telegram_session_string = session_data.telegram_session_string
    if session_data.is_active is not None:
        session.is_active = session_data.is_active
    if session_data.config_data is not None:
        session.config_data = session_data.config_data
    
    session.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session

@router.put("/userbot-sessions/{session_id}/toggle")
async def toggle_userbot_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Userbot-Session aktivieren/deaktivieren"""
    session = db.query(UserbotSession).filter(
        UserbotSession.id == session_id,
        UserbotSession.user_id == current_user.id
    ).first()
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session.is_active = not session.is_active
    session.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": f"Session {'aktiviert' if session.is_active else 'deaktiviert'}",
        "is_active": session.is_active
    }

@router.delete("/userbot-sessions/{session_id}")
async def delete_userbot_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Userbot-Session löschen"""
    session = db.query(UserbotSession).filter(
        UserbotSession.id == session_id,
        UserbotSession.user_id == current_user.id
    ).first()
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    db.delete(session)
    db.commit()
    
    return {"message": "Session erfolgreich gelöscht"}

@router.put("/userbot-sessions/{session_id}/extend")
async def extend_userbot_session(
    session_id: int,
    extension_data: dict,  # {"months": 1, "payment_amount": 29.99}
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Userbot-Session verlängern nach Zahlung"""
    session = db.query(UserbotSession).filter(
        UserbotSession.id == session_id,
        UserbotSession.user_id == current_user.id
    ).first()
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    # Aktualisiere Abonnement-Daten nach Zahlung
    now = datetime.utcnow()
    months = extension_data.get("months", 1)
    
    # Verlängere das Abonnement
    if session.subscription_end_date and session.subscription_end_date > now:
        # Verlängere von aktuellem Enddatum
        new_end_date = session.subscription_end_date + timedelta(days=30 * months)
    else:
        # Verlängere von jetzt
        new_end_date = now + timedelta(days=30 * months)
    
    session.subscription_status = "active"
    session.subscription_end_date = new_end_date
    session.last_payment_date = now
    session.next_payment_date = new_end_date
    session.auto_delete_date = new_end_date + timedelta(weeks=2)  # 2 Wochen nach Ablauf
    session.payment_reminder_sent = False
    session.deletion_warning_sent = False
    session.updated_at = now
    
    db.commit()
    db.refresh(session)
    
    return {
        "message": f"Session erfolgreich um {months} Monat(e) verlängert",
        "new_end_date": new_end_date,
        "auto_delete_date": session.auto_delete_date
    }

@router.get("/userbot-sessions/{session_id}/subscription-status")
async def get_session_subscription_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Abonnement-Status einer Session abrufen"""
    session = db.query(UserbotSession).filter(
        UserbotSession.id == session_id,
        UserbotSession.user_id == current_user.id
    ).first()
    
    if session is None:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    now = datetime.utcnow()
    
    # Berechne Status
    if session.subscription_end_date and session.subscription_end_date < now:
        days_overdue = (now - session.subscription_end_date).days
        status = "expired"
    else:
        days_overdue = 0
        status = session.subscription_status
    
    return {
        "session_id": session.id,
        "session_name": session.session_name,
        "subscription_status": status,
        "subscription_end_date": session.subscription_end_date,
        "next_payment_date": session.next_payment_date,
        "auto_delete_date": session.auto_delete_date,
        "days_overdue": days_overdue,
        "days_until_deletion": (session.auto_delete_date - now).days if session.auto_delete_date and session.auto_delete_date > now else 0
    }

@router.post("/userbot-sessions/cleanup-expired")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Abgelaufene Sessions bereinigen (nur für Admins)"""
    if not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Nur für Administratoren")
    
    now = datetime.utcnow()
    
    # Finde Sessions, die vor 2 Wochen abgelaufen sind
    expired_sessions = db.query(UserbotSession).filter(
        UserbotSession.auto_delete_date <= now,
        UserbotSession.subscription_status.in_(["expired", "pending_payment"])
    ).all()
    
    deleted_count = 0
    for session in expired_sessions:
        db.delete(session)
        deleted_count += 1
    
    db.commit()
    
    return {
        "message": f"{deleted_count} abgelaufene Sessions gelöscht",
        "deleted_sessions": deleted_count
    }

@router.get("/userbot-sessions/payment-reminders")
async def get_payment_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zahlungserinnerungen für Sessions abrufen"""
    now = datetime.utcnow()
    
    # Sessions, die bald ablaufen (7 Tage vor Ablauf)
    expiring_soon = db.query(UserbotSession).filter(
        UserbotSession.user_id == current_user.id,
        UserbotSession.subscription_status == "active",
        UserbotSession.subscription_end_date <= now + timedelta(days=7),
        UserbotSession.subscription_end_date > now,
        UserbotSession.payment_reminder_sent == False
    ).all()
    
    # Sessions, die abgelaufen sind
    expired = db.query(UserbotSession).filter(
        UserbotSession.user_id == current_user.id,
        UserbotSession.subscription_status.in_(["expired", "pending_payment"]),
        UserbotSession.subscription_end_date < now
    ).all()
    
    # Sessions, die bald gelöscht werden (3 Tage vor Löschung)
    deletion_warning = db.query(UserbotSession).filter(
        UserbotSession.user_id == current_user.id,
        UserbotSession.subscription_status.in_(["expired", "pending_payment"]),
        UserbotSession.auto_delete_date <= now + timedelta(days=3),
        UserbotSession.auto_delete_date > now,
        UserbotSession.deletion_warning_sent == False
    ).all()
    
    return {
        "expiring_soon": [
            {
                "session_id": session.id,
                "session_name": session.session_name,
                "days_until_expiry": (session.subscription_end_date - now).days
            } for session in expiring_soon
        ],
        "expired": [
            {
                "session_id": session.id,
                "session_name": session.session_name,
                "days_overdue": (now - session.subscription_end_date).days,
                "days_until_deletion": (session.auto_delete_date - now).days if session.auto_delete_date else 0
            } for session in expired
        ],
        "deletion_warning": [
            {
                "session_id": session.id,
                "session_name": session.session_name,
                "days_until_deletion": (session.auto_delete_date - now).days
            } for session in deletion_warning
        ]
    }

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
