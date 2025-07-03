from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Group
from pydantic import BaseModel
from typing import Optional, Any
import json
from app.routes.enhanced_group_management import EnhancedGroupManagement

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