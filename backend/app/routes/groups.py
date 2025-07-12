from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Any
from ..database import get_db
from ..models import Group, ForwardingGroupMapping, UserbotSession
from pydantic import BaseModel
import json
from .enhanced_group_management import EnhancedGroupManagement
import sys
import os

# Userbot-Service Import - Fallback wenn userbot_handler nicht existiert
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'userbot_service'))
    from userbot_handler import UserbotHandler
except ImportError:
    # Fallback: Erstelle eine Mock-Klasse
    class UserbotHandler:
        async def get_dialogs(self):
            return []

router = APIRouter(
    tags=["groups"]
)

class GroupUpdateRequest(BaseModel):
    welcome_text: Optional[str] = None
    night_mode: Optional[bool] = None
    night_mode_start: Optional[str] = None  # z.B. '22:00'
    night_mode_end: Optional[str] = None    # z.B. '08:00'
    badwords_enabled: Optional[bool] = None
    links_enabled: Optional[bool] = None
    info_settings: Optional[Any] = None  # z.B. dict
    forward_enabled: Optional[bool] = None
    roles: Optional[Any] = None  # z.B. dict
    settings: Optional[dict] = None  # für beliebige weitere Einstellungen

class GroupCreateRequest(BaseModel):
    group_id: str
    name: Optional[str] = None
    owner_id: int
    settings: Optional[dict] = None
    welcome_text: Optional[str] = None
    night_mode: Optional[bool] = None

class ForwardingMappingRequest(BaseModel):
    userbot_session_id: int
    source_group_id: str
    target_group_id: str

class DialogInfo(BaseModel):
    id: str
    title: str
    type: str  # "group" oder "channel"
    member_count: Optional[int] = None

@router.get("/dialogs")
async def get_available_dialogs():
    """Holt alle verfügbaren Gruppen/Kanäle vom Userbot"""
    try:
        userbot = UserbotHandler()
        dialogs = await userbot.get_dialogs()
        return {
            "status": "success",
            "dialogs": dialogs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Gruppen: {str(e)}")

@router.post("/forwarding-mapping")
def create_forwarding_mapping(data: ForwardingMappingRequest, db: Session = Depends(get_db)):
    """Erstellt eine neue Weiterleitungs-Mapping"""
    try:
        # Prüfe ob Userbot-Session existiert
        session = db.query(UserbotSession).filter(UserbotSession.id == data.userbot_session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Userbot-Session nicht gefunden")
        
        # Prüfe ob Mapping bereits existiert
        existing_mapping = db.query(ForwardingGroupMapping).filter(
            ForwardingGroupMapping.userbot_session_id == data.userbot_session_id,
            ForwardingGroupMapping.source_group_id == data.source_group_id,
            ForwardingGroupMapping.target_group_id == data.target_group_id
        ).first()
        
        if existing_mapping:
            raise HTTPException(status_code=400, detail="Weiterleitungs-Mapping existiert bereits")
        
        # Erstelle neues Mapping
        mapping = ForwardingGroupMapping(
            userbot_session_id=data.userbot_session_id,
            source_group_id=data.source_group_id,
            target_group_id=data.target_group_id,
            forwarding_active=True
        )
        
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        
        return {
            "status": "success",
            "message": "Weiterleitungs-Mapping erfolgreich erstellt",
            "mapping": {
                "id": mapping.id,
                "source_group_id": mapping.source_group_id,
                "target_group_id": mapping.target_group_id,
                "forwarding_active": mapping.forwarding_active
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Mappings: {str(e)}")

@router.get("/forwarding-mappings/{userbot_session_id}")
def get_forwarding_mappings(userbot_session_id: int, db: Session = Depends(get_db)):
    """Holt alle Weiterleitungs-Mappings für eine Userbot-Session"""
    try:
        mappings = db.query(ForwardingGroupMapping).filter(
            ForwardingGroupMapping.userbot_session_id == userbot_session_id
        ).all()
        
        return {
            "status": "success",
            "mappings": [
                {
                    "id": mapping.id,
                    "source_group_id": mapping.source_group_id,
                    "target_group_id": mapping.target_group_id,
                    "forwarding_active": mapping.forwarding_active,
                    "created_at": mapping.created_at.isoformat()
                }
                for mapping in mappings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Mappings: {str(e)}")

@router.delete("/forwarding-mapping/{mapping_id}")
def delete_forwarding_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Löscht eine Weiterleitungs-Mapping"""
    try:
        mapping = db.query(ForwardingGroupMapping).filter(ForwardingGroupMapping.id == mapping_id).first()
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping nicht gefunden")
        
        db.delete(mapping)
        db.commit()
        
        return {
            "status": "success",
            "message": "Weiterleitungs-Mapping erfolgreich gelöscht"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen des Mappings: {str(e)}")

@router.patch("/forwarding-mapping/{mapping_id}/toggle")
def toggle_forwarding_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Aktiviert/Deaktiviert eine Weiterleitungs-Mapping"""
    try:
        mapping = db.query(ForwardingGroupMapping).filter(ForwardingGroupMapping.id == mapping_id).first()
        if not mapping:
            raise HTTPException(status_code=404, detail="Mapping nicht gefunden")
        
        mapping.forwarding_active = not mapping.forwarding_active
        db.commit()
        db.refresh(mapping)
        
        return {
            "status": "success",
            "message": f"Weiterleitung {'aktiviert' if mapping.forwarding_active else 'deaktiviert'}",
            "forwarding_active": mapping.forwarding_active
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Umschalten des Mappings: {str(e)}")

@router.get("/{group_id}")
def get_group(group_id: int, db: Session = Depends(get_db)):
    group = db.query(Group).filter((Group.id == group_id) | (Group.group_id == str(group_id))).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
    settings_raw = group.__dict__["settings"]
    if isinstance(settings_raw, dict):
        settings = settings_raw
    else:
        try:
            settings = json.loads(settings_raw) if settings_raw else {}
        except Exception:
            settings = {}
    return {
        "id": group.id,
        "group_id": group.group_id,
        "name": group.name,
        "welcome_text": group.welcome_text,
        "night_mode": group.night_mode,
        "night_mode_start": settings.get("night_mode_start"),
        "night_mode_end": settings.get("night_mode_end"),
        "badwords_enabled": settings.get("badwords_enabled"),
        "links_enabled": settings.get("links_enabled"),
        "info_settings": settings.get("info_settings"),
        "forward_enabled": settings.get("forward_enabled"),
        "roles": settings.get("roles"),
        "settings": settings
    }

@router.patch("/{group_id}")
def update_group(group_id: int, data: GroupUpdateRequest, db: Session = Depends(get_db)):
    group = db.query(Group).filter((Group.id == group_id) | (Group.group_id == str(group_id))).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
    if data.welcome_text is not None:
        setattr(group, 'welcome_text', data.welcome_text)
    if data.night_mode is not None:
        setattr(group, 'night_mode', data.night_mode)
    settings_raw = group.__dict__["settings"]
    if isinstance(settings_raw, dict):
        settings = settings_raw
    else:
        try:
            settings = json.loads(settings_raw) if settings_raw else {}
        except Exception:
            settings = {}
    if data.night_mode_start is not None:
        settings["night_mode_start"] = data.night_mode_start
    if data.night_mode_end is not None:
        settings["night_mode_end"] = data.night_mode_end
    if data.badwords_enabled is not None:
        settings["badwords_enabled"] = data.badwords_enabled
    if data.links_enabled is not None:
        settings["links_enabled"] = data.links_enabled
    if data.info_settings is not None:
        settings["info_settings"] = data.info_settings
    if data.forward_enabled is not None:
        settings["forward_enabled"] = data.forward_enabled
    if data.roles is not None:
        settings["roles"] = data.roles
    if data.settings is not None:
        settings.update(data.settings)
    setattr(group, 'settings', settings)
    db.commit()
    db.refresh(group)
    return {
        "id": group.id,
        "group_id": group.group_id,
        "name": group.name,
        "welcome_text": group.welcome_text,
        "night_mode": group.night_mode,
        "night_mode_start": settings.get("night_mode_start"),
        "night_mode_end": settings.get("night_mode_end"),
        "badwords_enabled": settings.get("badwords_enabled"),
        "links_enabled": settings.get("links_enabled"),
        "info_settings": settings.get("info_settings"),
        "forward_enabled": settings.get("forward_enabled"),
        "roles": settings.get("roles"),
        "settings": settings
    }

@router.post("/")
def create_group(data: GroupCreateRequest, db: Session = Depends(get_db)):
    mgmt = EnhancedGroupManagement()
    group_data = {
        "group_id": data.group_id,
        "name": data.name,
        "settings": data.settings or {},
        "welcome_text": data.welcome_text,
        "night_mode": data.night_mode,
    }
    result = mgmt.create_group_with_dependencies(group_data, data.owner_id, db)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Fehler beim Anlegen der Gruppe"))
    return result 