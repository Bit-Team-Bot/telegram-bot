from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import PackageTemplate, Addon, AddonTier, PackageAddon
import json
from datetime import datetime
from typing import List

router = APIRouter(prefix="/admin/packages", tags=["admin-packages"])

# Admin-Status-Endpoint
@router.get("/status")
def admin_status():
    """Admin-Status-Endpoint für Authentifizierung"""
    return {
        "status": "admin_authenticated",
        "message": "Admin-Zugriff verfügbar",
        "timestamp": datetime.utcnow().isoformat()
    }

# Standard-Templates erstellen
@router.post("/templates/init")
def initialize_default_templates(db: Session = Depends(get_db)):
    """Erstellt Standard-Paket-Templates falls keine vorhanden sind"""
    
    # Prüfe ob bereits Templates existieren
    existing_templates = db.query(PackageTemplate).count()
    if existing_templates > 0:
        return {
            "message": f"Bereits {existing_templates} Templates vorhanden",
            "templates_created": 0
        }
    
    # Standard-Templates definieren
    default_templates = [
        {
            "name": "basic",
            "display_name": "Basic Paket",
            "package_type": "basic",
            "monthly_price": 9.99,
            "one_time_price": None,
            "features": {
                "basic_groups": True,
                "basic_analytics": True,
                "advanced_groups": False,
                "priority_support": False,
                "api_access": False,
                "unlimited_groups": False
            },
            "is_active": True
        },
        {
            "name": "pro",
            "display_name": "Pro Paket",
            "package_type": "pro",
            "monthly_price": 19.99,
            "one_time_price": None,
            "features": {
                "basic_groups": True,
                "basic_analytics": True,
                "advanced_groups": True,
                "priority_support": False,
                "api_access": False,
                "unlimited_groups": False
            },
            "is_active": True
        },
        {
            "name": "expert",
            "display_name": "Expert Paket",
            "package_type": "expert",
            "monthly_price": 39.99,
            "one_time_price": None,
            "features": {
                "basic_groups": True,
                "basic_analytics": True,
                "advanced_groups": True,
                "priority_support": True,
                "api_access": False,
                "unlimited_groups": False
            },
            "is_active": True
        },
        {
            "name": "lifetime",
            "display_name": "Lifetime Paket",
            "package_type": "lifetime",
            "monthly_price": None,
            "one_time_price": 999.99,
            "features": {
                "basic_groups": True,
                "basic_analytics": True,
                "advanced_groups": True,
                "priority_support": True,
                "api_access": True,
                "unlimited_groups": True
            },
            "is_active": True
        }
    ]
    
    # Templates erstellen
    created_count = 0
    for template_data in default_templates:
        # Prüfe ob Template bereits existiert
        existing = db.query(PackageTemplate).filter(PackageTemplate.name == template_data["name"]).first()
        if not existing:
            new_template = PackageTemplate(
                name=template_data["name"],
                display_name=template_data["display_name"],
                package_type=template_data["package_type"],
                monthly_price=template_data["monthly_price"],
                one_time_price=template_data["one_time_price"],
                features=json.dumps(template_data["features"]),
                is_active=template_data["is_active"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_template)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"{created_count} Standard-Templates erstellt",
        "templates_created": created_count,
        "templates": [
            {
                "name": t["name"],
                "display_name": t["display_name"],
                "package_type": t["package_type"]
            }
            for t in default_templates
        ]
    }

# --- Paket-Templates ---
@router.get("/templates", response_model=List[dict])
def list_package_templates(db: Session = Depends(get_db)):
    """Alle Paket-Templates auflisten"""
    # Lade alle Templates, nicht nur aktive
    templates = db.query(PackageTemplate).all()
    
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
        
        template_data = {
            "id": template.id,
            "name": template.name,
            "display_name": template.display_name,
            "package_type": template.package_type,
            "monthly_price": template.monthly_price,
            "one_time_price": template.one_time_price,
            "features": features,
            "is_active": template.is_active,
            "created_at": template.created_at.isoformat() if template.created_at is not None else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at is not None else None
        }
        result.append(template_data)
    
    return result

@router.post("/templates", response_model=dict)
def create_package_template(data: dict, db: Session = Depends(get_db)):
    """Neues Paket-Template anlegen"""
    # Prüfen ob Template mit diesem Namen bereits existiert
    existing = db.query(PackageTemplate).filter(PackageTemplate.name == data.get("name")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template mit diesem Namen existiert bereits")
    
    # Features als JSON speichern
    features = data.get("features", {})
    if not isinstance(features, dict):
        raise HTTPException(status_code=400, detail="Features müssen ein JSON-Objekt sein")
    
    template = PackageTemplate(
        name=data.get("name"),
        display_name=data.get("display_name"),
        package_type=data.get("package_type", "basic"),
        monthly_price=data.get("monthly_price"),
        one_time_price=data.get("one_time_price"),
        features=features,
        is_active=data.get("is_active", True)
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return {
        "id": template.id,
        "name": template.name,
        "display_name": template.display_name,
        "package_type": template.package_type,
        "monthly_price": template.monthly_price,
        "one_time_price": template.one_time_price,
        "features": template.features,
        "is_active": template.is_active,
        "created_at": template.created_at.isoformat() if template.created_at is not None else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at is not None else None
    }

@router.put("/templates/{template_id}", response_model=dict)
def update_package_template(template_id: int, data: dict, db: Session = Depends(get_db)):
    """Paket-Template bearbeiten"""
    template = db.query(PackageTemplate).filter(PackageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Paket-Template nicht gefunden")
    
    # Prüfen ob Name bereits von anderem Template verwendet wird
    if "name" in data and data["name"] != template.name:
        existing = db.query(PackageTemplate).filter(
            PackageTemplate.name == data["name"],
            PackageTemplate.id != template_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Template mit diesem Namen existiert bereits")
    
    # Felder aktualisieren
    if "name" in data:
        template.name = data["name"]
    if "display_name" in data:
        template.display_name = data["display_name"]
    if "package_type" in data:
        template.package_type = data["package_type"]
    if "monthly_price" in data:
        template.monthly_price = data["monthly_price"]
    if "one_time_price" in data:
        template.one_time_price = data["one_time_price"]
    if "features" in data:
        features = data["features"]
        if not isinstance(features, dict):
            raise HTTPException(status_code=400, detail="Features müssen ein JSON-Objekt sein")
        template.features = features
    if "is_active" in data:
        template.is_active = data["is_active"]
    
    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    
    return {
        "id": template.id,
        "name": template.name,
        "display_name": template.display_name,
        "package_type": template.package_type,
        "monthly_price": template.monthly_price,
        "one_time_price": template.one_time_price,
        "features": template.features,
        "is_active": template.is_active,
        "created_at": template.created_at.isoformat() if template.created_at is not None else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at is not None else None
    }

@router.delete("/templates/{template_id}")
def delete_package_template(template_id: int, db: Session = Depends(get_db)):
    """Paket-Template löschen"""
    template = db.query(PackageTemplate).filter(PackageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Paket-Template nicht gefunden")
    
    # Prüfen ob Template noch verwendet wird
    active_packages = db.query(PackageTemplate).filter(
        PackageTemplate.id == template_id
    ).count()
    
    if active_packages > 0:
        # Statt löschen nur deaktivieren
        template.is_active = False
        template.updated_at = datetime.utcnow()
        db.commit()
        return {"ok": True, "message": "Template wurde deaktiviert (wird noch verwendet)"}
    else:
        # Komplett löschen
        db.delete(template)
        db.commit()
        return {"ok": True, "message": "Template wurde gelöscht"}

# --- Add-ons ---
@router.get("/addons", response_model=List[dict])
def list_addons(db: Session = Depends(get_db)):
    """Alle Add-ons auflisten"""
    addons = db.query(Addon).filter(Addon.is_active == True).all()
    
    result = []
    for addon in addons:
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
                "description": tier.description,
                "is_active": tier.is_active
            })
        
        addon_data = {
            "id": addon.id,
            "name": addon.name,
            "display_name": addon.display_name,
            "description": addon.description,
            "monthly_price": addon.monthly_price,
            "one_time_price": addon.one_time_price,
            "is_active": addon.is_active,
            "tiers": tiers_data,
            "created_at": addon.created_at.isoformat() if addon.created_at is not None else None,
            "updated_at": addon.updated_at.isoformat() if addon.updated_at is not None else None
        }
        result.append(addon_data)
    
    return result

@router.post("/addons", response_model=dict)
def create_addon(data: dict, db: Session = Depends(get_db)):
    """Neues Add-on anlegen"""
    # Prüfen ob Add-on mit diesem Namen bereits existiert
    existing = db.query(Addon).filter(Addon.name == data.get("name")).first()
    if existing:
        raise HTTPException(status_code=400, detail="Add-on mit diesem Namen existiert bereits")
    
    addon = Addon(
        name=data.get("name"),
        display_name=data.get("display_name"),
        description=data.get("description"),
        monthly_price=data.get("monthly_price", 0.0),
        one_time_price=data.get("one_time_price"),
        is_active=data.get("is_active", True)
    )
    
    db.add(addon)
    db.flush()  # Um die ID zu bekommen
    
    # Tiers hinzufügen falls vorhanden
    tiers_data = data.get("tiers", [])
    for tier_data in tiers_data:
        tier = AddonTier(
            addon_id=addon.id,
            level=tier_data.get("level"),
            price=tier_data.get("price", 0.0),
            description=tier_data.get("description"),
            is_active=tier_data.get("is_active", True)
        )
        db.add(tier)
    
    db.commit()
    db.refresh(addon)
    
    return {
        "id": addon.id,
        "name": addon.name,
        "display_name": addon.display_name,
        "description": addon.description,
        "monthly_price": addon.monthly_price,
        "one_time_price": addon.one_time_price,
        "is_active": addon.is_active,
        "created_at": addon.created_at.isoformat() if addon.created_at is not None else None,
        "updated_at": addon.updated_at.isoformat() if addon.updated_at is not None else None
    }

@router.put("/addons/{addon_id}", response_model=dict)
def update_addon(addon_id: int, data: dict, db: Session = Depends(get_db)):
    """Add-on bearbeiten"""
    addon = db.query(Addon).filter(Addon.id == addon_id).first()
    if not addon:
        raise HTTPException(status_code=404, detail="Add-on nicht gefunden")
    
    # Prüfen ob Name bereits von anderem Add-on verwendet wird
    if "name" in data and data["name"] != addon.name:
        existing = db.query(Addon).filter(
            Addon.name == data["name"],
            Addon.id != addon_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Add-on mit diesem Namen existiert bereits")
    
    # Felder aktualisieren
    if "name" in data:
        addon.name = data["name"]
    if "display_name" in data:
        addon.display_name = data["display_name"]
    if "description" in data:
        addon.description = data["description"]
    if "monthly_price" in data:
        addon.monthly_price = data["monthly_price"]
    if "one_time_price" in data:
        addon.one_time_price = data["one_time_price"]
    if "is_active" in data:
        addon.is_active = data["is_active"]
    
    addon.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(addon)
    
    return {
        "id": addon.id,
        "name": addon.name,
        "display_name": addon.display_name,
        "description": addon.description,
        "monthly_price": addon.monthly_price,
        "one_time_price": addon.one_time_price,
        "is_active": addon.is_active,
        "created_at": addon.created_at.isoformat() if addon.created_at is not None else None,
        "updated_at": addon.updated_at.isoformat() if addon.updated_at is not None else None
    }

@router.delete("/addons/{addon_id}")
def delete_addon(addon_id: int, db: Session = Depends(get_db)):
    """Add-on löschen"""
    addon = db.query(Addon).filter(Addon.id == addon_id).first()
    if not addon:
        raise HTTPException(status_code=404, detail="Add-on nicht gefunden")
    
    # Prüfen ob Add-on noch verwendet wird
    active_user_addons = db.query(PackageAddon).filter(PackageAddon.addon_id == addon_id).count()
    
    if active_user_addons > 0:
        # Statt löschen nur deaktivieren
        addon.is_active = False
        addon.updated_at = datetime.utcnow()
        db.commit()
        return {"ok": True, "message": "Add-on wurde deaktiviert (wird noch verwendet)"}
    else:
        # Komplett löschen
        db.delete(addon)
        db.commit()
        return {"ok": True, "message": "Add-on wurde gelöscht"}

# --- Feature-Matrix & Add-on-Freischaltung ---
@router.get("/templates/{template_id}/features", response_model=dict)
def get_feature_matrix(template_id: int, db: Session = Depends(get_db)):
    """Feature-Matrix eines Pakets anzeigen"""
    template = db.query(PackageTemplate).filter(PackageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Paket-Template nicht gefunden")
    
    # Feature-Matrix korrekt verarbeiten
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
        PackageAddon.package_template_id == template_id
    ).all()
    
    available_addons = []
    for pa in package_addons:
        addon = db.query(Addon).filter(Addon.id == pa.addon_id).first()
        if addon:
            available_addons.append({
                "id": addon.id,
                "name": addon.name,
                "display_name": addon.display_name,
                "is_enabled": pa.is_enabled
            })
    
    return {
        "template_id": template.id,
        "template_name": template.name,
        "template_display_name": template.display_name,
        "features": features,
        "available_addons": available_addons
    }

@router.put("/templates/{template_id}/features", response_model=dict)
def update_feature_matrix(template_id: int, data: dict, db: Session = Depends(get_db)):
    """Feature-Matrix eines Pakets bearbeiten"""
    template = db.query(PackageTemplate).filter(PackageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Paket-Template nicht gefunden")
    
    features = data.get("features")
    if not isinstance(features, dict):
        raise HTTPException(status_code=400, detail="Features müssen ein JSON-Objekt sein")
    
    template.features = features
    template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(template)
    
    return {
        "template_id": template.id,
        "template_name": template.name,
        "template_display_name": template.display_name,
        "features": template.features,
        "message": "Feature-Matrix wurde aktualisiert"
    }

@router.put("/templates/{template_id}/addons/{addon_id}", response_model=dict)
def enable_addon_for_package(template_id: int, addon_id: int, enabled: bool, db: Session = Depends(get_db)):
    """Add-on für ein Paket aktivieren/deaktivieren"""
    template = db.query(PackageTemplate).filter(PackageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Paket-Template nicht gefunden")
    
    addon = db.query(Addon).filter(Addon.id == addon_id).first()
    if not addon:
        raise HTTPException(status_code=404, detail="Add-on nicht gefunden")
    
    # PackageAddon Verknüpfung finden oder erstellen
    package_addon = db.query(PackageAddon).filter(
        PackageAddon.package_template_id == template_id,
        PackageAddon.addon_id == addon_id
    ).first()
    
    if package_addon:
        package_addon.is_enabled = enabled
    else:
        package_addon = PackageAddon(
            package_template_id=template_id,
            addon_id=addon_id,
            is_enabled=enabled
        )
        db.add(package_addon)
    
    db.commit()
    
    return {
        "ok": True,
        "message": f"Add-on '{addon.display_name}' wurde für Paket '{template.display_name}' {'aktiviert' if enabled else 'deaktiviert'}"
    } 