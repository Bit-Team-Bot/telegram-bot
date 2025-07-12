from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import (
    PackageTemplate, Addon, AddonTier, PackageAddon, 
    User, Package, UserAddon, Payment
)
from .auth import get_current_user
from typing import List, Optional
import json
from datetime import datetime

router = APIRouter(prefix="/user/packages", tags=["user-packages"])

# --- Verfügbare Pakete für User ---
@router.get("/available", response_model=List[dict])
def get_available_packages(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Alle verfügbaren Pakete für den User anzeigen"""
    templates = db.query(PackageTemplate).filter(PackageTemplate.is_active == True).all()
    
    result = []
    for template in templates:
        # Features korrekt verarbeiten
        features = template.features
        if isinstance(features, str):
            try:
                features = json.loads(features)
            except:
                features = {}
        elif features is None:
            features = {}
        
        # Verfügbare Add-ons für dieses Paket holen
        package_addons = db.query(PackageAddon).filter(
            PackageAddon.package_template_id == template.id,
            PackageAddon.is_enabled == True
        ).all()
        
        available_addons = []
        for pa in package_addons:
            addon = db.query(Addon).filter(Addon.id == pa.addon_id, Addon.is_active == True).first()
            if addon:
                # Tiers für dieses Add-on holen
                tiers = db.query(AddonTier).filter(
                    AddonTier.addon_id == addon.id,
                    AddonTier.is_active == True
                ).all()
                
                tiers_data = []
                for tier in tiers:
                    tiers_data.append({
                        "id": tier.id,
                        "level": tier.level,
                        "price": tier.price,
                        "description": tier.description
                    })
                
                available_addons.append({
                    "id": addon.id,
                    "name": addon.name,
                    "display_name": addon.display_name,
                    "description": addon.description,
                    "monthly_price": addon.monthly_price,
                    "one_time_price": addon.one_time_price,
                    "tiers": tiers_data
                })
        
        template_data = {
            "id": template.id,
            "name": template.name,
            "display_name": template.display_name,
            "package_type": template.package_type,
            "monthly_price": template.monthly_price,
            "one_time_price": template.one_time_price,
            "features": features,
            "available_addons": available_addons
        }
        result.append(template_data)
    
    return result

# --- Aktuelles User-Paket ---
@router.get("/current", response_model=dict)
def get_current_package(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Aktuelles Paket des Users anzeigen"""
    # Aktives Paket des Users finden
    active_package = db.query(Package).filter(
        Package.user_id == current_user.id,
        getattr(Package, 'status', None) == "active"
    ).first()
    
    # Superadmin/Partner: Immer Zugriff, auch ohne aktives Paket
    if active_package is None and not (getattr(current_user, 'is_superadmin', False) or getattr(current_user, 'role', None) == 'partner'):
        return {
            "has_package": False,
            "package": None,
            "template": None,
            "features": {},
            "addons": []
        }
    
    # Template-Informationen holen
    template = None
    features = {}
    if active_package is not None and getattr(active_package, 'template_id', None) is not None:
        template = db.query(PackageTemplate).filter(PackageTemplate.id == active_package.template_id).first()
        if template is not None:
            features = template.features
            if isinstance(features, str):
                try:
                    features = json.loads(features)
                except:
                    features = {}
            elif features is None:
                features = {}
    
    # User-Add-ons holen
    user_addons = db.query(UserAddon).filter(
        UserAddon.user_id == current_user.id,
        UserAddon.status == "active"
    ).all()
    
    addons_data = []
    for ua in user_addons:
        addon = db.query(Addon).filter(Addon.id == ua.addon_id).first()
        if addon is not None:
            tier = None
            if getattr(ua, 'tier_id', None) is not None:
                tier = db.query(AddonTier).filter(AddonTier.id == ua.tier_id).first()
            
            addons_data.append({
                "id": addon.id,
                "name": addon.name,
                "display_name": addon.display_name,
                "description": addon.description,
                "tier": {
                    "id": tier.id,
                    "level": tier.level,
                    "price": tier.price,
                    "description": tier.description
                } if tier is not None else None,
                "start_date": ua.start_date.isoformat() if getattr(ua, 'start_date', None) is not None else None,
                "end_date": ua.end_date.isoformat() if getattr(ua, 'end_date', None) is not None else None
            })
    
    return {
        "has_package": True,
        "package": {
            "id": active_package.id if active_package is not None else 0,
            "name": active_package.name if active_package is not None else "Superadmin/Partner-Zugriff",
            "price": active_package.price if active_package is not None else 0,
            "duration_days": active_package.duration_days if active_package is not None else 0,
            "status": active_package.status if active_package is not None else "active",
            "start_date": active_package.start_date.isoformat() if active_package is not None and getattr(active_package, 'start_date', None) is not None else None,
            "end_date": active_package.end_date.isoformat() if active_package is not None and getattr(active_package, 'end_date', None) is not None else None
        },
        "template": {
            "id": template.id if template is not None else 0,
            "name": template.name if template is not None else "Superadmin/Partner-Zugriff",
            "display_name": template.display_name if template is not None else "Superadmin/Partner-Zugriff",
            "package_type": template.package_type if template is not None else "all"
        } if template is not None or (getattr(current_user, 'is_superadmin', False) or getattr(current_user, 'role', None) == 'partner') else None,
        "features": features,
        "addons": addons_data
    }

# --- Add-on buchen ---
@router.post("/addons/{addon_id}/book", response_model=dict)
def book_addon(addon_id: int, tier_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add-on für den User buchen"""
    # Prüfen ob User ein aktives Paket hat ODER Superadmin/Partner ist
    active_package = db.query(Package).filter(
        Package.user_id == current_user.id,
        getattr(Package, 'status', None) == "active"
    ).first()
    
    if not (active_package or current_user.is_superadmin or current_user.role == 'partner'):
        raise HTTPException(status_code=400, detail="Sie benötigen ein aktives Paket, um Add-ons zu buchen")
    
    # Add-on prüfen
    addon = db.query(Addon).filter(Addon.id == addon_id, Addon.is_active == True).first()
    if not addon:
        raise HTTPException(status_code=400, detail="Add-on nicht gefunden")
    
    # Prüfen ob Add-on für das aktuelle Paket verfügbar ist
    if active_package and active_package.template_id:
        package_addon = db.query(PackageAddon).filter(
            PackageAddon.package_template_id == active_package.template_id,
            PackageAddon.addon_id == addon_id,
            PackageAddon.is_enabled == True
        ).first()
        
        if not package_addon and not (current_user.is_superadmin or current_user.role == 'partner'):
            raise HTTPException(status_code=400, detail="Dieses Add-on ist für Ihr Paket nicht verfügbar")
    # Wenn kein aktives Paket, aber Superadmin/Partner: Add-on trotzdem erlauben
    
    # Prüfen ob User das Add-on bereits hat
    existing_addon = db.query(UserAddon).filter(
        UserAddon.user_id == current_user.id,
        UserAddon.addon_id == addon_id,
        UserAddon.status == "active"
    ).first()
    
    if existing_addon:
        raise HTTPException(status_code=400, detail="Sie haben dieses Add-on bereits gebucht")
    
    # Tier prüfen falls angegeben
    tier = None
    if tier_id:
        tier = db.query(AddonTier).filter(
            AddonTier.id == tier_id,
            AddonTier.addon_id == addon_id,
            AddonTier.is_active == True
        ).first()
        if not tier:
            raise HTTPException(status_code=404, detail="Tier nicht gefunden")
    
    # Preis berechnen
    price = addon.monthly_price
    if tier:
        price = tier.price
    
    # UserAddon erstellen
    user_addon = UserAddon(
        user_id=current_user.id,
        addon_id=addon_id,
        tier_id=tier.id if tier else None,
        status="active",
        start_date=datetime.utcnow()
    )
    
    db.add(user_addon)
    
    # Payment erstellen (optional: für Superadmin/Partner auf 0 setzen)
    payment = Payment(
        user_id=current_user.id,
        addon_id=addon_id,
        amount=0 if (current_user.is_superadmin or current_user.role == 'partner') else price,
        status="pending"
    )
    
    db.add(payment)
    db.commit()
    db.refresh(user_addon)
    
    return {
        "ok": True,
        "message": f"Add-on '{addon.display_name}' wurde erfolgreich gebucht",
        "user_addon_id": user_addon.id,
        "payment_id": payment.id,
        "price": 0 if (current_user.is_superadmin or current_user.role == 'partner') else price
    }

# --- Add-on kündigen ---
@router.delete("/addons/{addon_id}/cancel", response_model=dict)
def cancel_addon(addon_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Add-on für den User kündigen"""
    user_addon = db.query(UserAddon).filter(
        UserAddon.user_id == current_user.id,
        UserAddon.addon_id == addon_id,
        UserAddon.status == "active"
    ).first()
    
    if user_addon is None:
        raise HTTPException(status_code=404, detail="Add-on nicht gefunden")
    
    # Add-on deaktivieren
    setattr(user_addon, 'status', "inactive")
    setattr(user_addon, 'end_date', datetime.utcnow())
    
    db.commit()
    
    return {
        "ok": True,
        "message": "Add-on wurde erfolgreich gekündigt"
    }

# --- User-Add-ons auflisten ---
@router.get("/addons", response_model=List[dict])
def list_user_addons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Alle Add-ons des Users auflisten"""
    user_addons = db.query(UserAddon).filter(UserAddon.user_id == current_user.id).all()
    
    result = []
    for ua in user_addons:
        addon = db.query(Addon).filter(Addon.id == ua.addon_id).first()
        if addon is not None:
            tier = None
            if getattr(ua, 'tier_id', None) is not None:
                tier = db.query(AddonTier).filter(AddonTier.id == ua.tier_id).first()
            
            result.append({
                "id": ua.id,
                "addon": {
                    "id": addon.id,
                    "name": addon.name,
                    "display_name": addon.display_name,
                    "description": addon.description
                },
                "tier": {
                    "id": tier.id,
                    "level": tier.level,
                    "price": tier.price,
                    "description": tier.description
                } if tier is not None else None,
                "status": ua.status,
                "start_date": ua.start_date.isoformat() if getattr(ua, 'start_date', None) is not None else None,
                "end_date": ua.end_date.isoformat() if getattr(ua, 'end_date', None) is not None else None
            })
    
    return result 