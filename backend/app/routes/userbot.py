"""
Zentrale Userbot-Routen für das Backend
Vereinigt alle Userbot-API-Endpunkte
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, UserbotSession, ForwardingGroupMapping
from ..routes.auth import get_current_user
from ..services.userbot_service import userbot_service
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/userbot", tags=["userbot"])

class PhoneNumberRequest(BaseModel):
    phone_number: str

class CodeRequest(BaseModel):
    phone_number: str
    code: str
    password: Optional[str] = None

class UserbotSessionCreateRequest(BaseModel):
    phone: str
    session_name: str
    session_type: str
    telegram_session_string: str
    is_active: bool = True

# ----------- ZENTRALE USERBOT-ROUTEN -----------

@router.post("/create-session")
async def create_userbot_session(
    request: PhoneNumberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Neue Userbot-Session erstellen"""
    try:
        logger.info(f"🔧 Erstelle Userbot-Session für User {current_user.id}, Telefon: {request.phone_number}")
        
        # Prüfe ob User ein aktives Userbot-Paket hat
        if not current_user.package_id:
            raise HTTPException(
                status_code=403,
                detail="Sie benötigen ein aktives Userbot-Paket"
            )
        
        # Userbot-Service aufrufen
        result = await userbot_service.create_session(request.phone_number)
        
        if result.get("success"):
            logger.info(f"✅ Userbot-Session erstellt für {request.phone_number}")
            return result
        else:
            logger.error(f"❌ Userbot-Session-Erstellung fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Session-Erstellung fehlgeschlagen"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler bei Session-Erstellung: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei Session-Erstellung: {str(e)}")

@router.post("/send-code")
async def send_userbot_code(
    request: PhoneNumberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verifizierungscode senden"""
    try:
        logger.info(f"🔧 Sende Code für User {current_user.id}, Telefon: {request.phone_number}")
        
        # Userbot-Service aufrufen
        result = await userbot_service.send_code(request.phone_number)
        
        if result.get("success"):
            logger.info(f"✅ Code gesendet für {request.phone_number}")
            return result
        else:
            logger.error(f"❌ Code-Versand fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Code-Versand fehlgeschlagen"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Code-Versand: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Code-Versand: {str(e)}")

@router.post("/verify-code")
async def verify_userbot_code(
    request: CodeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Code verifizieren"""
    try:
        logger.info(f"[DEBUG] Eingehende Payload: {request.dict()}")
        logger.info(f"[DEBUG] Aktueller User: {current_user.id}, Paket: {current_user.package_id}")
        logger.info(f"🔧 Verifiziere Code für User {current_user.id}, Telefon: {request.phone_number}")
        
        # Vor dem Anlegen/Aktualisieren: Alle alten Sessions für User+Telefon deaktivieren
        db.query(UserbotSession).filter(
            UserbotSession.user_id == current_user.id,
            UserbotSession.phone == request.phone_number
        ).update({UserbotSession.is_active: False})
        db.commit()

        # Userbot-Service aufrufen
        result = await userbot_service.verify_code(
            request.phone_number, 
            request.code, 
            request.password
        )
        
        if result.get("success"):
            logger.info(f"✅ Code verifiziert für {request.phone_number}")
            
            # Session in Datenbank speichern/aktualisieren
            try:
                existing_session = db.query(UserbotSession).filter(
                    UserbotSession.user_id == current_user.id,
                    UserbotSession.phone == request.phone_number
                ).first()
                
                if existing_session:
                    # Session aktualisieren
                    existing_session.is_active = True
                    existing_session.telegram_session_string = result.get("session_string")
                    existing_session.updated_at = datetime.utcnow()
                    # Telegram-ID immer mit speichern
                    existing_session.telegram_id = current_user.telegram_id
                    db.commit()
                    logger.info(f"✅ Userbot-Session aktualisiert für User {current_user.id}")
                else:
                    # Neue Session erstellen
                    new_session = UserbotSession(
                        user_id=current_user.id,
                        session_name="Userbot-Session",
                        session_type="message_forwarding",
                        phone=request.phone_number,
                        telegram_session_string=result.get("session_string"),
                        is_active=True,
                        telegram_id=current_user.telegram_id
                    )
                    db.add(new_session)
                    db.commit()
                    logger.info(f"✅ Neue Userbot-Session erstellt für User {current_user.id}")
                    
            except Exception as db_error:
                logger.error(f"❌ Datenbankfehler bei Session-Speicherung: {db_error}")
                # Session trotzdem als erfolgreich markieren
                
            return result
        else:
            logger.error(f"❌ Code-Verifikation fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Code-Verifikation fehlgeschlagen"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler bei Code-Verifikation: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei Code-Verifikation: {str(e)}")

@router.get("/session-status/{phone_number}")
async def get_userbot_session_status(
    phone_number: str,
    db: Session = Depends(get_db)
):
    """Session-Status abrufen - OHNE Authentifizierung für Frontend-Zugriff"""
    try:
        logger.info(f"🔧 Prüfe Session-Status für Telefon: {phone_number} (ohne Auth)")
        
        # Userbot-Service aufrufen
        result = await userbot_service.get_session_status(phone_number)
        
        if result.get("success"):
            logger.info(f"✅ Session-Status abgerufen für {phone_number}")
            return result
        else:
            logger.error(f"❌ Session-Status-Abruf fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Session-Status nicht verfügbar"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Session-Status-Abruf: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Session-Status-Abruf: {str(e)}")

@router.post("/disconnect-session")
async def disconnect_userbot_session(
    request: PhoneNumberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Session trennen"""
    try:
        logger.info(f"🔧 Trenne Session für User {current_user.id}, Telefon: {request.phone_number}")
        
        # Userbot-Service aufrufen
        result = await userbot_service.disconnect_session(request.phone_number)
        
        if result.get("success"):
            # Session in Datenbank deaktivieren
            try:
                session = db.query(UserbotSession).filter(
                    UserbotSession.user_id == current_user.id,
                    UserbotSession.phone == request.phone_number
                ).first()
                
                if session:
                    session.is_active = False
                    session.updated_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"✅ Userbot-Session deaktiviert für User {current_user.id}")
                    
            except Exception as db_error:
                logger.error(f"❌ Datenbankfehler bei Session-Deaktivierung: {db_error}")
                
            logger.info(f"✅ Session getrennt für {request.phone_number}")
            return result
        else:
            logger.error(f"❌ Session-Trennung fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Session-Trennung fehlgeschlagen"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler bei Session-Trennung: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei Session-Trennung: {str(e)}")

@router.get("/chats/{phone_number}")
async def get_userbot_chats(
    phone_number: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chats für Session abrufen"""
    try:
        logger.info(f"🔧 Hole Chats für User {current_user.id}, Telefon: {phone_number}")
        
        # Userbot-Service aufrufen
        result = await userbot_service.get_chats(phone_number)
        
        if result.get("success"):
            logger.info(f"✅ Chats abgerufen für {phone_number}")
            return result
        else:
            logger.error(f"❌ Chat-Abruf fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Chats nicht verfügbar"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Chat-Abruf: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Chat-Abruf: {str(e)}")

@router.get("/active-sessions-count")
async def get_active_sessions_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Anzahl aktiver Sessions abrufen"""
    try:
        logger.info(f"🔧 Hole aktive Sessions-Count für User {current_user.id}")
        
        # Userbot-Service aufrufen
        result = await userbot_service.get_active_sessions_count()
        
        if result.get("success"):
            logger.info(f"✅ Aktive Sessions-Count abgerufen")
            return result
        else:
            logger.error(f"❌ Sessions-Count-Abruf fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Sessions-Count nicht verfügbar"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Sessions-Count-Abruf: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Sessions-Count-Abruf: {str(e)}")

@router.get("/all-sessions")
async def get_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Sessions abrufen"""
    try:
        logger.info(f"🔧 Hole alle Sessions für User {current_user.id}")
        
        # Userbot-Service aufrufen
        result = await userbot_service.get_all_sessions()
        
        if result.get("success"):
            logger.info(f"✅ Alle Sessions abgerufen")
            return result
        else:
            logger.error(f"❌ Sessions-Abruf fehlgeschlagen: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Sessions nicht verfügbar"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim Sessions-Abruf: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Sessions-Abruf: {str(e)}") 

@router.get("/my-sessions")
async def get_my_userbot_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Alle Userbot-Sessions des eingeloggten Users abrufen"""
    try:
        logger.info(f"🔧 Hole Userbot-Sessions für User {current_user.id}")
        sessions = db.query(UserbotSession).filter(UserbotSession.user_id == current_user.id).all()
        return {
            "success": True,
            "sessions": [
                {
                    "id": s.id,
                    "phone": s.phone,
                    "session_name": s.session_name,
                    "session_type": s.session_type,
                    "is_active": s.is_active,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                    "updated_at": s.updated_at.isoformat() if s.updated_at else None
                } for s in sessions
            ]
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Userbot-Sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Userbot-Sessions: {str(e)}") 

@router.post("/sessions")
async def create_userbot_session_full(
    data: UserbotSessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Legt eine Userbot-Session mit allen gewünschten Feldern für den eingeloggten User an."""
    try:
        new_session = UserbotSession(
            user_id=current_user.id,
            phone=data.phone,
            session_name=data.session_name,
            session_type=data.session_type,
            telegram_session_string=data.telegram_session_string,
            is_active=data.is_active
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return {
            "success": True,
            "session": {
                "id": new_session.id,
                "user_id": new_session.user_id,
                "phone": new_session.phone,
                "session_name": new_session.session_name,
                "session_type": new_session.session_type,
                "telegram_session_string": new_session.telegram_session_string,
                "is_active": new_session.is_active,
                "created_at": new_session.created_at,
                "updated_at": new_session.updated_at
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Userbot-Session: {e}") 

 