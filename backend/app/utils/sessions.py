import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models import UserSession
from backend.app.schemas import SessionCreate
from typing import Optional

SESSION_DURATION_DAYS = 30  # Standard-Gültigkeit einer Session


def create_user_session(db: Session, session_data: SessionCreate) -> UserSession:
    """
    Erstellt eine neue User-Session und gibt das Session-Objekt zurück.
    """
    # Deaktiviere alte Sessions für diesen User/Telegram-ID
    db.query(UserSession).filter(
        UserSession.user_id == session_data.user_id,
        UserSession.telegram_id == session_data.telegram_id,
        UserSession.is_active == True
    ).update({UserSession.is_active: False})
    db.commit()

    session_token = secrets.token_urlsafe(32)
    now = datetime.utcnow()
    expires_at = now + timedelta(days=SESSION_DURATION_DAYS)

    session = UserSession(
        user_id=session_data.user_id,
        telegram_id=session_data.telegram_id,
        session_token=session_token,
        ip_address=session_data.ip_address,
        user_agent=session_data.user_agent,
        is_active=True,
        created_at=now,
        expires_at=expires_at,
        last_activity=now
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def validate_session_token(db: Session, session_token: str, telegram_id: str) -> Optional[UserSession]:
    """
    Prüft, ob ein Session-Token gültig und aktiv ist und zur Telegram-ID passt.
    Gibt das Session-Objekt zurück oder None.
    """
    session = db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.telegram_id == telegram_id,
        UserSession.is_active == True,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    if session is not None:
        session.last_activity = datetime.utcnow()
        db.commit()
        db.refresh(session)
    return session


def invalidate_user_sessions(db: Session, user_id: int, telegram_id: str = None):
    """
    Setzt alle Sessions eines Users (optional für eine bestimmte Telegram-ID) auf inaktiv.
    """
    query = db.query(UserSession).filter(UserSession.user_id == user_id, UserSession.is_active == True)
    if telegram_id:
        query = query.filter(UserSession.telegram_id == telegram_id)
    query.update({UserSession.is_active: False})
    db.commit()


def cleanup_expired_sessions(db: Session) -> int:
    """
    Löscht alle abgelaufenen UserSessions (expires_at < jetzt oder is_active=False) und gibt die Anzahl zurück.
    """
    now = datetime.utcnow()
    expired_sessions = db.query(UserSession).filter(
        (UserSession.expires_at < now) | (UserSession.is_active == False)
    ).all()
    count = len(expired_sessions)
    for session in expired_sessions:
        db.delete(session)
    db.commit()
    return count 