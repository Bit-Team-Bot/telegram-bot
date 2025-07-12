from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, Package, UserbotSession
from ..auth import get_current_user
from pydantic import BaseModel
from ..schemas import UserbotSessionCreate
import logging

router = APIRouter()

class PackageResponse(BaseModel):
    id: int
    name: str
    price: float
    duration_days: int
    features: List[str]
    featured: bool = False
    status: str = "available"

    class Config:
        orm_mode = True

@router.get("/", response_model=List[PackageResponse])
async def get_packages(db: Session = Depends(get_db)):
    """Alle verfügbaren Pakete aus der Datenbank abrufen"""
    db_packages = db.query(Package).all()
    result = []
    for pkg in db_packages:
        # Features als Liste verarbeiten (kann als JSON-String gespeichert sein)
        features = []
        raw_features = pkg.features
        if hasattr(raw_features, 'value'):
            raw_features = raw_features.value
        if isinstance(raw_features, str) and raw_features:
            import json
            try:
                features = json.loads(raw_features)
                if isinstance(features, dict):
                    features = list(features.values())
                elif not isinstance(features, list):
                    features = [str(features)]
            except Exception:
                features = [str(raw_features)]
        result.append({
            "id": pkg.id,
            "name": pkg.name,
            "price": pkg.price,
            "duration_days": pkg.duration_days,
            "features": features,
            "featured": False,
            "status": pkg.status or "available"
        })
    return result

@router.get("/{package_id}", response_model=PackageResponse)
async def get_package(package_id: int, db: Session = Depends(get_db)):
    """Ein spezifisches Paket abrufen"""
    packages_data = await get_packages(db)
    
    for package in packages_data:
        if package["id"] == package_id:
            return package
    
    raise HTTPException(status_code=404, detail="Paket nicht gefunden")

@router.post("/{package_id}/purchase")
async def purchase_package(
    package_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ein Paket für den aktuellen Benutzer kaufen"""
    # Prüfe ob Paket existiert
    package = await get_package(package_id, db)
    
    # Hier würde die Zahlungslogik implementiert werden
    # Für jetzt erstellen wir nur eine einfache Bestätigung

    # Userbot-Session automatisch anlegen, falls noch keine existiert
    try:
        existing_session = db.query(UserbotSession).filter(
            UserbotSession.user_id == current_user.id
        ).first()
        if not existing_session:
            session_data = UserbotSessionCreate(
                session_name="Auto-Session",
                session_type="message_forwarding",
                phone=current_user.phone or "",
                is_active=True
            )
            new_session = UserbotSession(
                user_id=current_user.id,
                session_name=session_data.session_name,
                session_type=session_data.session_type,
                phone=session_data.phone,
                is_active=True
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            logging.info(f"Userbot-Session automatisch für User {current_user.id} nach Paketkauf angelegt.")
    except Exception as e:
        logging.error(f"Fehler beim automatischen Anlegen der Userbot-Session: {e}")

    return {
        "status": "success",
        "message": f"Paket {package['name']} erfolgreich gekauft",
        "package_id": package_id,
        "user_id": current_user.id,
        "amount": package["price"]
    }
