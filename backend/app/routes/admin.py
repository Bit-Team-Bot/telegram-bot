from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.schemas import (
    UserCreate, UserUpdate, UserResponse,
    PackageCreate, PackageUpdate, PackageResponse,
    FeatureCreate, FeatureUpdate, FeatureResponse,
    SignalGroupCreate, SignalGroupUpdate, SignalGroupResponse,
    PaymentCreate, PaymentUpdate, PaymentResponse,
    UserbotSessionCreate, UserbotSessionUpdate, UserbotSessionResponse,
    SignalGroupSubscriptionCreate, SignalGroupSubscriptionUpdate, SignalGroupSubscriptionResponse,
    SignalThemeCreate, SignalThemeUpdate, SignalThemeResponse
)
from backend.app.auth import get_current_user
from backend.app.models import User, Package, Payment, SignalGroup, UserbotSession, SignalTheme, SignalGroupSubscription
from backend.app.schemas import PaymentStatus
import json
from datetime import datetime
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["admin"])

# Benutzer-Routen
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Benutzer abrufen (nur für Administratoren)"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return db.query(User).all()

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Neuen Benutzer erstellen (nur für Administratoren)"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    # Prüfen ob Telegram ID bereits existiert
    if db.query(User).filter(User.telegram_id == user_data.telegram_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram ID bereits registriert"
        )
    
    # Neuen Benutzer erstellen
    new_user = User(
        telegram_id=user_data.telegram_id,
        phone=user_data.phone,
        role=user_data.role.value,
        is_active=user_data.is_active
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}/toggle-status", response_model=UserResponse)
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Benutzerstatus umschalten (aktiv/inaktiv)"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden"
        )
    
    # Status umschalten
    setattr(user, 'is_active', not bool(user.is_active))
    db.commit()
    db.refresh(user)
    return user

# Paket-Routen
@router.get("/packages", response_model=List[PackageResponse])
async def get_packages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Pakete abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return db.query(Package).all()

@router.post("/packages", response_model=PackageResponse)
async def create_package(
    package_data: PackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Neues Paket erstellen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    if db.query(Package).filter(Package.name == package_data.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paketname bereits vergeben"
        )
    
    new_package = Package(
        name=package_data.name,
        price=package_data.price,
        duration_days=package_data.duration_days,
        features=package_data.features
    )
    
    db.add(new_package)
    db.commit()
    db.refresh(new_package)
    return new_package

# Zahlungs-Routen
@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Zahlungen abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return db.query(Payment).all()

@router.post("/payments/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Zahlung bestätigen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zahlung nicht gefunden"
        )
    
    setattr(payment, 'status', PaymentStatus.COMPLETED.value)
    db.commit()
    db.refresh(payment)
    return payment

# Signalgruppen-Routen
@router.get("/signal-groups", response_model=List[SignalGroupResponse])
async def get_signal_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Signalgruppen abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return db.query(SignalGroup).all()

@router.post("/signal-groups", response_model=SignalGroupResponse)
async def create_signal_group(
    signal_group_data: SignalGroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Neue Signalgruppe erstellen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    if db.query(SignalGroup).filter(SignalGroup.name == signal_group_data.name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signalgruppenname bereits vergeben"
        )
    
    new_signal_group = SignalGroup(
        name=signal_group_data.name,
        description=signal_group_data.description,
        partner_id=signal_group_data.partner_id,
        price_1_group=signal_group_data.price_1_group,
        price_2_groups=signal_group_data.price_2_groups,
        price_3_groups=signal_group_data.price_3_groups,
        price_4_groups=signal_group_data.price_4_groups,
        price_5_groups=signal_group_data.price_5_groups,
        is_active=signal_group_data.is_active
    )
    
    db.add(new_signal_group)
    db.commit()
    db.refresh(new_signal_group)
    return new_signal_group

@router.put("/signal-groups/{signal_group_id}", response_model=SignalGroupResponse)
async def update_signal_group(
    signal_group_id: int,
    signal_group_data: SignalGroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Signalgruppe bearbeiten"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    signal_group = db.query(SignalGroup).filter(SignalGroup.id == signal_group_id).first()
    if not signal_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signalgruppe nicht gefunden"
        )
    
    # Prüfen ob Name bereits von anderer Gruppe verwendet wird
    if signal_group_data.name and signal_group_data.name != signal_group.name:
        existing = db.query(SignalGroup).filter(
            SignalGroup.name == signal_group_data.name,
            SignalGroup.id != signal_group_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signalgruppenname bereits vergeben"
            )
    
    # Felder aktualisieren mit setattr
    if signal_group_data.name is not None:
        setattr(signal_group, 'name', signal_group_data.name)
    if signal_group_data.description is not None:
        setattr(signal_group, 'description', signal_group_data.description)
    if signal_group_data.partner_id is not None:
        setattr(signal_group, 'partner_id', signal_group_data.partner_id)
    if signal_group_data.price_1_group is not None:
        setattr(signal_group, 'price_1_group', signal_group_data.price_1_group)
    if signal_group_data.price_2_groups is not None:
        setattr(signal_group, 'price_2_groups', signal_group_data.price_2_groups)
    if signal_group_data.price_3_groups is not None:
        setattr(signal_group, 'price_3_groups', signal_group_data.price_3_groups)
    if signal_group_data.price_4_groups is not None:
        setattr(signal_group, 'price_4_groups', signal_group_data.price_4_groups)
    if signal_group_data.price_5_groups is not None:
        setattr(signal_group, 'price_5_groups', signal_group_data.price_5_groups)
    if signal_group_data.is_active is not None:
        setattr(signal_group, 'is_active', signal_group_data.is_active)
    
    db.commit()
    db.refresh(signal_group)
    return signal_group

@router.delete("/signal-groups/{signal_group_id}")
async def delete_signal_group(
    signal_group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Signalgruppe löschen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    signal_group = db.query(SignalGroup).filter(SignalGroup.id == signal_group_id).first()
    if not signal_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signalgruppe nicht gefunden"
        )
    
    db.delete(signal_group)
    db.commit()
    return {"message": "Signalgruppe erfolgreich gelöscht"}

# Userbot-Session-Routen
@router.get("/userbot-sessions", response_model=List[UserbotSessionResponse])
async def get_userbot_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Userbot-Sessions abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return db.query(UserbotSession).all()

@router.post("/userbot-sessions", response_model=UserbotSessionResponse)
async def create_userbot_session(
    session_data: UserbotSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Neue Userbot-Session erstellen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    new_session = UserbotSession(
        user_id=current_user.id,  # Verwende current_user.id statt session_data.user_id
        phone=session_data.phone,
        session_name=session_data.session_name,
        session_type=session_data.session_type,
        telegram_session_string=session_data.telegram_session_string,
        is_active=session_data.is_active
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.put("/userbot-sessions/{session_id}", response_model=UserbotSessionResponse)
async def update_userbot_session(
    session_id: int,
    session_data: UserbotSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Userbot-Session bearbeiten"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    session = db.query(UserbotSession).filter(UserbotSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Userbot-Session nicht gefunden"
        )
    
    # Felder aktualisieren mit setattr
    if session_data.phone is not None:
        setattr(session, 'phone', session_data.phone)
    if session_data.session_name is not None:
        setattr(session, 'session_name', session_data.session_name)
    if session_data.session_type is not None:
        setattr(session, 'session_type', session_data.session_type)
    if session_data.telegram_session_string is not None:
        setattr(session, 'telegram_session_string', session_data.telegram_session_string)
    if session_data.is_active is not None:
        setattr(session, 'is_active', session_data.is_active)
    
    db.commit()
    db.refresh(session)
    return session

@router.delete("/userbot-sessions/{session_id}")
async def delete_userbot_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Userbot-Session löschen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    session = db.query(UserbotSession).filter(UserbotSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Userbot-Session nicht gefunden"
        )
    
    db.delete(session)
    db.commit()
    return {"message": "Userbot-Session erfolgreich gelöscht"}

@router.delete("/userbot-sessions/by-phone/{phone}")
async def delete_userbot_sessions_by_phone(phone: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Löscht alle Userbot-Sessions für eine Telefonnummer (nur für Superadmins)"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    deleted = db.query(UserbotSession).filter(UserbotSession.phone == phone).delete()
    db.commit()
    return {"success": True, "deleted": deleted}

# Signalgruppen-Abonnement-Routen
@router.get("/signal-group-subscriptions", response_model=List[SignalGroupSubscriptionResponse])
async def get_signal_group_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Signalgruppen-Abonnements abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    return db.query(SignalGroupSubscription).all()

@router.post("/signal-group-subscriptions", response_model=SignalGroupSubscriptionResponse)
async def create_signal_group_subscription(
    subscription_data: SignalGroupSubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Neues Signalgruppen-Abonnement erstellen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    new_subscription = SignalGroupSubscription(
        user_id=current_user.id,  # Verwende current_user.id statt subscription_data.user_id
        signal_group_id=subscription_data.signal_group_id,
        group_count=subscription_data.group_count,
        status=subscription_data.status,
        end_date=subscription_data.end_date
    )
    
    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)
    return new_subscription

# Thematische Gruppen-Routen
@router.get("/signal-themes", response_model=List[SignalThemeResponse])
async def get_signal_themes(
    signal_group_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle thematischen Gruppen abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    query = db.query(SignalTheme)
    if signal_group_id:
        query = query.filter(SignalTheme.signal_group_id == signal_group_id)
    
    return query.all()

@router.post("/signal-themes", response_model=SignalThemeResponse)
async def create_signal_theme(
    theme_data: SignalThemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Neue thematische Gruppe erstellen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    # Prüfe ob Signal-Gruppe existiert
    signal_group = db.query(SignalGroup).filter(SignalGroup.id == theme_data.signal_group_id).first()
    if not signal_group:
        raise HTTPException(status_code=404, detail="Signal-Gruppe nicht gefunden")
    
    new_theme = SignalTheme(
        signal_group_id=theme_data.signal_group_id,
        name=theme_data.name,
        description=theme_data.description,
        keywords=theme_data.keywords,
        price_monthly=theme_data.price_monthly,
        is_active=theme_data.is_active
    )
    
    db.add(new_theme)
    db.commit()
    db.refresh(new_theme)
    return new_theme

@router.put("/signal-themes/{theme_id}", response_model=SignalThemeResponse)
async def update_signal_theme(
    theme_id: int,
    theme_data: SignalThemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Thematische Gruppe bearbeiten"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    theme = db.query(SignalTheme).filter(SignalTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(status_code=404, detail="Thematische Gruppe nicht gefunden")
    
    # Aktualisiere Felder mit setattr
    if theme_data.name is not None:
        setattr(theme, 'name', theme_data.name)
    if theme_data.description is not None:
        setattr(theme, 'description', theme_data.description)
    if theme_data.keywords is not None:
        setattr(theme, 'keywords', theme_data.keywords)
    if theme_data.price_monthly is not None:
        setattr(theme, 'price_monthly', theme_data.price_monthly)
    if theme_data.is_active is not None:
        setattr(theme, 'is_active', theme_data.is_active)
    
    setattr(theme, 'updated_at', datetime.utcnow())
    db.commit()
    db.refresh(theme)
    return theme

@router.delete("/signal-themes/{theme_id}")
async def delete_signal_theme(
    theme_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Signal-Theme löschen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    theme = db.query(SignalTheme).filter(SignalTheme.id == theme_id).first()
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal-Theme nicht gefunden"
        )
    
    db.delete(theme)
    db.commit()
    return {"message": "Signal-Theme erfolgreich gelöscht"}

# Userbot-Session-Verknüpfung für Signal-Gruppen
@router.put("/signal-groups/{signal_group_id}/link-userbot")
async def link_userbot_to_signal_group(
    signal_group_id: int,
    link_data: dict,  # {"userbot_session_id": 123, "target_groups": ["-100123", "-100456"]}
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Userbot-Session mit Signal-Gruppe verknüpfen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    signal_group = db.query(SignalGroup).filter(SignalGroup.id == signal_group_id).first()
    if not signal_group:
        raise HTTPException(status_code=404, detail="Signal-Gruppe nicht gefunden")
    
    # Prüfe Userbot-Session
    if link_data.get("userbot_session_id"):
        userbot_session = db.query(UserbotSession).filter(
            UserbotSession.id == link_data["userbot_session_id"]
        ).first()
        if not userbot_session:
            raise HTTPException(status_code=404, detail="Userbot-Session nicht gefunden")
    
    # Aktualisiere Verknüpfung mit setattr
    setattr(signal_group, 'userbot_session_id', link_data.get("userbot_session_id"))
    setattr(signal_group, 'target_groups', json.dumps(link_data.get("target_groups", [])))
    setattr(signal_group, 'updated_at', datetime.utcnow())
    
    db.commit()
    db.refresh(signal_group)
    
    return {
        "message": "Userbot-Session erfolgreich verknüpft",
        "signal_group_id": signal_group.id,
        "userbot_session_id": signal_group.userbot_session_id
    }

@router.get("/signal-groups/{signal_group_id}/themes")
async def get_signal_group_themes(
    signal_group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Themen einer Signal-Gruppe abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    themes = db.query(SignalTheme).filter(
        SignalTheme.signal_group_id == signal_group_id,
        SignalTheme.is_active == True
    ).all()
    
    return themes 

# ===== FEHLENDE ADMIN ENDPUNKTE =====

@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin-Statistiken abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    try:
        # Benutzer-Statistiken
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        new_users_today = db.query(User).filter(
            User.created_at >= datetime.utcnow().date()
        ).count()
        
        # Paket-Statistiken
        total_packages = db.query(Package).count()
        active_packages = db.query(Package).filter(Package.status == "active").count()
        
        # Zahlungs-Statistiken
        total_payments = db.query(Payment).count()
        total_revenue = db.query(Payment).filter(Payment.status == "completed").with_entities(
            func.sum(Payment.amount)
        ).scalar() or 0
        
        # Signalgruppen-Statistiken
        total_signal_groups = db.query(SignalGroup).count()
        active_signal_groups = db.query(SignalGroup).filter(SignalGroup.is_active == True).count()
        
        # Userbot-Session-Statistiken
        total_userbot_sessions = db.query(UserbotSession).count()
        active_userbot_sessions = db.query(UserbotSession).filter(UserbotSession.is_active == True).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "new_today": new_users_today
            },
            "packages": {
                "total": total_packages,
                "active": active_packages
            },
            "payments": {
                "total": total_payments,
                "revenue": float(total_revenue)
            },
            "signal_groups": {
                "total": total_signal_groups,
                "active": active_signal_groups
            },
            "userbot_sessions": {
                "total": total_userbot_sessions,
                "active": active_userbot_sessions
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Admin-Statistiken: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Statistiken: {str(e)}")

@router.get("/settings")
async def get_admin_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin-Einstellungen abrufen"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    try:
        # System-Einstellungen (Mock-Daten für jetzt)
        settings = {
            "system": {
                "maintenance_mode": False,
                "registration_enabled": True,
                "userbot_enabled": True,
                "payment_enabled": True
            },
            "notifications": {
                "email_notifications": True,
                "telegram_notifications": True,
                "admin_alerts": True
            },
            "security": {
                "session_timeout_hours": 24,
                "max_login_attempts": 5,
                "require_2fa": False
            },
            "features": {
                "userbot_sessions": True,
                "signal_groups": True,
                "forwarding": True,
                "auto_reply": True
            },
            "limits": {
                "max_userbot_sessions_per_user": 5,
                "max_signal_groups_per_user": 10,
                "max_forwarding_mappings_per_session": 20
            }
        }
        
        return settings
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Admin-Einstellungen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Einstellungen: {str(e)}")

@router.put("/settings")
async def update_admin_settings(
    settings_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Admin-Einstellungen aktualisieren"""
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    try:
        # Hier würden die Einstellungen in der DB gespeichert werden
        # Für jetzt geben wir nur eine Bestätigung zurück
        
        return {
            "success": True,
            "message": "Admin-Einstellungen erfolgreich aktualisiert",
            "settings": settings_data
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Admin-Einstellungen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Einstellungen: {str(e)}") 