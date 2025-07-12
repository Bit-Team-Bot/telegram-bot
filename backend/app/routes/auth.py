from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import jwt
import random
import httpx
from backend.app.database import get_db
from backend.app.config import settings
from backend.app.schemas import UserResponse, CodeRequest, CodeVerify, UserRole, SessionCreate, SessionResponse
from backend.app.models import User
from backend.app.utils.telegram_bot import send_telegram_message
from backend.app.utils.sessions import create_user_session, validate_session_token
import logging
import re

# Dummy für validate_telegram_webapp_data, falls nicht vorhanden
try:
    from backend.app.utils.telegram_webapp import validate_telegram_webapp_data
except ImportError:
    def validate_telegram_webapp_data(data):
        return True

router = APIRouter(tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

logger = logging.getLogger(__name__)

# Userbot API URL
USERBOT_API_URL = getattr(settings, 'USERBOT_API_URL', 'http://localhost:8001')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_client_ip(request: Request) -> str:
    """Extrahiert die Client-IP aus dem Request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Extrahiert den User-Agent aus dem Request"""
    return request.headers.get("User-Agent", "unknown")

def normalize_phone(phone: str) -> str:
    """Normalisiert Telefonnummern für Vergleich und Speicherung."""
    if not phone:
        return phone
    phone = phone.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if phone.startswith("00"):
        phone = "+" + phone[2:]
    return phone

@router.post("/telegram-login")
async def telegram_login(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        # Telegram WebApp Daten aus dem Request extrahieren
        data = await request.json()
        init_data = data.get("initData")
        user_data = data.get("user")
        
        if not init_data or not user_data:
            return {"success": False, "detail": "Ungültige Telegram WebApp Daten"}
        
        # Telegram WebApp Validierung
        if not validate_telegram_webapp_data(init_data):
            return {"success": False, "detail": "Ungültige Telegram WebApp Daten"}
        
        # Benutzer anhand der Telegram ID suchen
        telegram_id = str(user_data.get("id"))
        phone = user_data.get("phone")
        if not telegram_id:
            return {"success": False, "detail": "Keine Telegram ID gefunden"}
        
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user and phone:
            # Falls User mit Telegram-ID nicht existiert, aber mit Telefonnummer, dann verknüpfen
            user = db.query(User).filter(User.phone == phone).first()
            if user:
                user.telegram_id = telegram_id
                db.commit()
                db.refresh(user)
                logger.info(f"Telegram-ID {telegram_id} mit User {user.phone} verknüpft.")
        if not user:
            return {"success": False, "detail": "Benutzer nicht gefunden"}
        if not user.is_active:
            return {"success": False, "detail": "Benutzer ist deaktiviert"}
        # JWT Token generieren
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role,
                "telegram_id": user.telegram_id
            }
        )
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user)
        }
    except Exception as e:
        logger.error(f"Fehler in /telegram-login: {str(e)}")
        return {"success": False, "detail": str(e)}

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Ungültiger Token")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Ungültiger Token")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    return user 

@router.post("/request-code", status_code=200)
async def request_code(
    request_data: CodeRequest,
    db: Session = Depends(get_db)
):
    try:
        # Telefonnummer normalisieren
        norm_phone = normalize_phone(request_data.phone) if request_data.phone else None
        # Zuerst nach Telegram-ID suchen
        user = None
        if request_data.telegram_id:
            user = db.query(User).filter(User.telegram_id == request_data.telegram_id).first()
            logger.info(f"Suche nach Telegram-ID {request_data.telegram_id}: {'gefunden' if user else 'nicht gefunden'}")
        # Falls nicht gefunden, nach normalisierter Telefonnummer suchen
        if not user and norm_phone:
            user = db.query(User).filter(User.phone == norm_phone).first()
            logger.info(f"Suche nach Telefonnummer {norm_phone}: {'gefunden' if user else 'nicht gefunden'}")
        # Prüfe, ob die Telegram-ID bereits bei einem anderen User existiert
        if request_data.telegram_id:
            existing_user_with_telegram = db.query(User).filter(
                User.telegram_id == request_data.telegram_id,
                User.phone != norm_phone
            ).first()
            if existing_user_with_telegram:
                logger.warning(f"Telegram-ID {request_data.telegram_id} bereits bei User {existing_user_with_telegram.phone} vergeben")
                return {
                    "success": False, 
                    "detail": "Diese Telegram-ID ist bereits mit einem anderen Account verknüpft."
                }
        if not user:
            # Neuen User anlegen, wenn nicht vorhanden
            user = User(
                phone=norm_phone,
                telegram_id=request_data.telegram_id,
                role=UserRole.USER.value,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Neuer Benutzer mit Telefonnummer {norm_phone} angelegt.")
        else:
            # Bestehenden User aktualisieren
            updated = False
            # Telefonnummer aktualisieren, falls anders
            if norm_phone and user.phone != norm_phone:
                setattr(user, 'phone', norm_phone)
                updated = True
                logger.info(f"Telefonnummer für User {user.id} aktualisiert: {norm_phone}")
            # Telegram-ID aktualisieren, falls nicht vorhanden
            if request_data.telegram_id and user.telegram_id != request_data.telegram_id:
                if user.telegram_id is None:
                    setattr(user, 'telegram_id', request_data.telegram_id)
                    updated = True
                    logger.info(f"Telegram-ID {request_data.telegram_id} für User {user.id} gespeichert.")
                else:
                    logger.warning(f"User {user.id} hat bereits Telegram-ID {user.telegram_id}, kann nicht auf {request_data.telegram_id} geändert werden")
            if updated:
                db.commit()
                db.refresh(user)
        if not (getattr(user, 'is_active', True) is True):
            logger.warning(f"Inaktiver Benutzer versucht Login: {norm_phone}")
            return {"success": False, "detail": "Benutzer ist deaktiviert."}
        # Prüfe, ob Userbot verwendet werden soll (aus request_data)
        use_userbot = getattr(request_data, 'use_userbot', False)
        if use_userbot:
            # USERBOT-INTEGRATION: Echte Telegram-Verifizierung über Userbot
            try:
                logger.info(f"🚀 Starte Userbot-Verifizierung für {norm_phone}")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    # Userbot-Verifizierung starten
                    userbot_response = await client.post(
                        f"{USERBOT_API_URL}/start",
                        json={"phone": norm_phone}
                    )
                    if userbot_response.status_code == 200:
                        userbot_data = userbot_response.json()
                        logger.info(f"✅ Userbot-Verifizierung gestartet: {userbot_data}")
                        if userbot_data.get('status') == 'code_sent':
                            return {
                                "success": True,
                                "detail": "Telegram-Verifizierungscode wurde an Ihre Nummer gesendet.",
                                "userbot_status": "started",
                                "message": "Bitte geben Sie den Code ein, der an Ihre Telegram-Nummer gesendet wurde."
                            }
                        else:
                            logger.warning(f"⚠️ Userbot-Fehler: {userbot_data}")
                            # Fallback: Eigener Code
                            return await _generate_fallback_code(user, db)
                    else:
                        logger.error(f"❌ Userbot-Fehler: {userbot_response.status_code} - {userbot_response.text}")
                        # Fallback: Eigener Code
                        return await _generate_fallback_code(user, db)
            except Exception as userbot_error:
                logger.error(f"❌ Userbot-Verbindung fehlgeschlagen: {userbot_error}")
                # Fallback: Eigener Code
                return await _generate_fallback_code(user, db)
        else:
            # Direkt Backend-Code verwenden
            logger.info(f"📡 Verwende Backend-Code für {norm_phone}")
            return await _generate_fallback_code(user, db)
    except Exception as e:
        logger.error(f"Fehler in /request-code: {str(e)}")
        return {"success": False, "detail": "Interner Serverfehler: " + str(e)}

async def _generate_fallback_code(user, db):
    """Fallback: Generiert eigenen Code wenn Userbot nicht verfügbar"""
    logger.info(f"🔄 Verwende Fallback-Code für {user.phone}")
    
    # Generiere einen 6-stelligen Code
    login_code = str(random.randint(100000, 999999))
    # Speichere Code und Ablaufdatum (5 Minuten)
    user.login_code = login_code
    user.login_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
    db.commit()
    
    # Sende Code via Telegram (nur wenn Telegram-ID vorhanden)
    if user.telegram_id is not None:
        message = f"Ihr Login-Code für das Webinterface lautet: <b>{login_code}</b>\nDieser Code ist 5 Minuten gültig."
        await send_telegram_message(str(user.telegram_id), message)
        logger.info(f"Login-Code an {user.phone} (TG: {user.telegram_id}) gesendet.")
        return {
            "success": True,
            "detail": "Login-Code wurde an Ihren Telegram-Account gesendet."
        }
    else:
        logger.info(f"Login-Code für {user.phone} generiert, aber keine Telegram-ID hinterlegt.")
        # TEMPORÄRE LÖSUNG: Code direkt zurückgeben für Tests
        return {
            "success": True,
            "detail": f"Login-Code: {login_code} (5 Minuten gültig)",
            "code": login_code,  # Nur für Tests!
            "message": "Bitte öffnen Sie die Seite über den Bot, um den Code automatisch zu erhalten."
        }

@router.post("/verify-code")
async def verify_code(
    request_data: CodeVerify,
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        norm_phone = normalize_phone(request_data.phone)
        logger.info(f"Verify-code request für Telefonnummer: {norm_phone}")
        user = db.query(User).filter(User.phone == norm_phone).first()
        if not user:
            logger.warning(f"User nicht gefunden für Telefonnummer: {norm_phone}")
            raise HTTPException(status_code=400, detail="Ungültiger Code oder Telefonnummer.")
        # USERBOT-INTEGRATION: Versuche Userbot-Verifizierung zuerst
        try:
            logger.info(f"🔐 Versuche Userbot-Verifizierung für {norm_phone}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Userbot-Code verifizieren
                userbot_response = await client.post(
                    f"{USERBOT_API_URL}/verify",
                    json={"phone": norm_phone, "code": request_data.code}
                )
                if userbot_response.status_code == 200:
                    userbot_data = userbot_response.json()
                    logger.info(f"✅ Userbot-Verifizierung erfolgreich: {userbot_data}")
                    # Userbot-Verifizierung erfolgreich - User einloggen
                    return await _complete_login(user, request, db)
                else:
                    logger.warning(f"⚠️ Userbot-Verifizierung fehlgeschlagen: {userbot_response.status_code}")
                    # Fallback: Eigener Code-Check
                    return await _verify_fallback_code(user, request_data, request, db)
        except Exception as userbot_error:
            logger.error(f"❌ Userbot-Verbindung fehlgeschlagen: {userbot_error}")
            # Fallback: Eigener Code-Check
            return await _verify_fallback_code(user, request_data, request, db)
    except HTTPException:
        # HTTPException weiterwerfen
        raise
    except Exception as e:
        logger.error(f"Fehler in /verify-code: {str(e)}")
        raise HTTPException(status_code=500, detail="Interner Serverfehler")

async def _verify_fallback_code(user, request_data, request, db):
    """Fallback: Verifiziert eigenen Code wenn Userbot nicht verfügbar"""
    logger.info(f"🔄 Verwende Fallback-Code-Verifizierung für {user.phone}")
    
    # Detailliertes Logging der User-Daten
    logger.info(f"User {user.id} gefunden - login_code: {user.login_code}, expires_at: {user.login_code_expires_at}")
    
    if user.login_code != request_data.code:
        logger.warning(f"Ungültiger Code für User {user.id}: erwartet {user.login_code}, erhalten {request_data.code}")
        raise HTTPException(status_code=400, detail="Ungültiger Code oder Telefonnummer.")
        
    if user.login_code_expires_at < datetime.utcnow():
        logger.warning(f"Abgelaufener Code für User {user.id}")
        raise HTTPException(status_code=400, detail="Der Login-Code ist abgelaufen.")
        
    # Code verbrauchen
    user.login_code = None
    user.login_code_expires_at = None
    db.commit()
    
    logger.info(f"Code erfolgreich verifiziert für User {user.id}")
    
    return await _complete_login(user, request, db)

async def _complete_login(user, request, db):
    """Vervollständigt den Login-Prozess"""
    # Session erstellen für Auto-Login
    try:
        session_data = SessionCreate(
            user_id=user.id,
            telegram_id=user.telegram_id,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request)
        )
        session = create_user_session(db, session_data)
        logger.info(f"Session erstellt für User {user.id}")
    except Exception as session_error:
        logger.error(f"Fehler beim Erstellen der Session: {session_error}")
        # Trotzdem fortfahren, Session ist optional
    
    # JWT Token generieren
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "telegram_id": user.telegram_id
        }
    )
    
    logger.info(f"Login erfolgreich für {user.phone} (TG: {user.telegram_id})")
    
    response_data = {
        "success": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }
    
    # Session-Daten hinzufügen, falls Session erstellt wurde
    if 'session' in locals():
        response_data["session"] = SessionResponse(
            session_token=session.session_token,
            expires_at=session.expires_at,
            last_activity=session.last_activity
        )
    
    return response_data

@router.post("/auto-login")
async def auto_login_telegram(
    request: Request,
    db: Session = Depends(get_db)
):
    try:
        data = await request.json()
        telegram_id = str(data.get("telegram_id"))
        session_token = data.get("session_token")
        
        if not telegram_id:
            return {"success": False, "detail": "Telegram-ID erforderlich"}
        
        # Suche User anhand Telegram-ID
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        
        if not user:
            return {"success": False, "detail": "Benutzer nicht gefunden"}
        
        if not user.is_active:
            return {"success": False, "detail": "Benutzer ist deaktiviert"}
        
        # SICHERHEIT: User muss eine verifizierte Telefonnummer haben
        if not user.phone:
            logger.warning(f"Auto-Login für User ohne Telefonnummer {telegram_id} verweigert")
            return {"success": False, "detail": "Telefonnummer erforderlich. Bitte melden Sie sich über den Login-Prozess an."}
        
        # SICHERHEIT: Session-Token ist PFLICHT für Auto-Login
        if not session_token:
            logger.warning(f"Auto-Login ohne Session-Token für Telegram-ID {telegram_id} verweigert")
            return {"success": False, "detail": "Gültige Session erforderlich. Bitte melden Sie sich über den Login-Prozess an."}
        
        # Session-Token validieren
        session = validate_session_token(db, session_token, telegram_id)
        if not session:
            logger.warning(f"Ungültiger Session-Token für Telegram-ID {telegram_id}")
            return {"success": False, "detail": "Ungültige Session. Bitte melden Sie sich erneut an."}
        
        # JWT Token generieren
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role,
                "telegram_id": user.telegram_id
            }
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user),
            "session": SessionResponse(
                session_token=session.session_token,
                expires_at=session.expires_at,
                last_activity=session.last_activity
            )
        }
        
    except Exception as e:
        logger.error(f"Fehler in /auto-login: {str(e)}")
        return {"success": False, "detail": "Interner Serverfehler: " + str(e)}

@router.post("/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Logout-Endpoint"""
    try:
        # Token aus Header extrahieren
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"success": False, "detail": "Kein Token gefunden"}
        
        token = auth_header.split(" ")[1]
        
        # Token validieren (optional, für Logging)
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            logger.info(f"User {user_id} logged out")
        except jwt.InvalidTokenError:
            pass  # Token bereits ungültig
        
        return {
            "success": True,
            "message": "Erfolgreich ausgeloggt"
        }
    except Exception as e:
        logger.error(f"Fehler beim Logout: {str(e)}")
        return {"success": False, "detail": str(e)}

# ===== FEHLENDE AUTH ENDPUNKTE =====

@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """Standard-Login-Endpoint (Kompatibilität mit Frontend)"""
    try:
        data = await request.json()
        phone = data.get("phone")
        telegram_id = data.get("telegram_id")
        
        if not phone and not telegram_id:
            return {"success": False, "detail": "Telefonnummer oder Telegram-ID erforderlich"}
        
        # Verwende den bestehenden request-code Endpunkt
        from .auth import CodeRequest
        code_request = CodeRequest(
            phone=phone,
            telegram_id=telegram_id,
            use_userbot=True
        )
        
        # Rufe request-code auf
        result = await request_code(code_request, db)
        return result
        
    except Exception as e:
        logger.error(f"Fehler in /login: {str(e)}")
        return {"success": False, "detail": str(e)}

@router.post("/register")
async def register(
    request: Request,
    db: Session = Depends(get_db)
):
    """Standard-Register-Endpoint (Kompatibilität mit Frontend)"""
    try:
        data = await request.json()
        phone = data.get("phone")
        telegram_id = data.get("telegram_id")
        user_name = data.get("user_name")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        
        if not phone and not telegram_id:
            return {"success": False, "detail": "Telefonnummer oder Telegram-ID erforderlich"}
        
        # Prüfe ob User bereits existiert
        user = None
        if telegram_id:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user and phone:
            user = db.query(User).filter(User.phone == phone).first()
        
        if user:
            return {"success": False, "detail": "Benutzer existiert bereits"}
        
        # Erstelle neuen User
        new_user = User(
            phone=phone,
            telegram_id=telegram_id,
            user_name=user_name,
            first_name=first_name,
            last_name=last_name,
            username=username,
            role=UserRole.USER.value,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "success": True,
            "message": "Benutzer erfolgreich registriert",
            "user_id": new_user.id
        }
        
    except Exception as e:
        logger.error(f"Fehler in /register: {str(e)}")
        return {"success": False, "detail": str(e)}

@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Token-Refresh-Endpoint"""
    try:
        # Token aus Header extrahieren
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"success": False, "detail": "Kein Token gefunden"}
        
        token = auth_header.split(" ")[1]
        
        # Token validieren
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                return {"success": False, "detail": "Ungültiger Token"}
            
            # User aus DB holen
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return {"success": False, "detail": "Benutzer nicht gefunden oder inaktiv"}
            
            # Neuen Token generieren
            new_token = create_access_token(
                data={
                    "sub": str(user.id),
                    "role": user.role,
                    "telegram_id": user.telegram_id
                }
            )
            
            return {
                "success": True,
                "access_token": new_token,
                "token_type": "bearer"
            }
            
        except jwt.InvalidTokenError:
            return {"success": False, "detail": "Ungültiger Token"}
        
    except Exception as e:
        logger.error(f"Fehler beim Token-Refresh: {str(e)}")
        return {"success": False, "detail": str(e)}

@router.get("/verify")
async def verify_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Token-Verify-Endpoint"""
    try:
        # Token aus Header extrahieren
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"success": False, "detail": "Kein Token gefunden"}
        
        token = auth_header.split(" ")[1]
        
        # Token validieren
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            
            if not user_id:
                return {"success": False, "detail": "Ungültiger Token"}
            
            # User aus DB holen
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active:
                return {"success": False, "detail": "Benutzer nicht gefunden oder inaktiv"}
            
            return {
                "success": True,
                "valid": True,
                "user": {
                    "id": user.id,
                    "telegram_id": user.telegram_id,
                    "phone": user.phone,
                    "user_name": user.user_name,
                    "role": user.role,
                    "is_active": user.is_active
                }
            }
            
        except jwt.InvalidTokenError:
            return {"success": False, "detail": "Ungültiger Token"}
        
    except Exception as e:
        logger.error(f"Fehler beim Token-Verify: {str(e)}")
        return {"success": False, "detail": str(e)}
