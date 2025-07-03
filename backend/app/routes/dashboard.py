from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from app.routes.auth import get_current_user
from app.models import User, Package, Payment
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt Dashboard-Statistiken für den aktuellen User zurück"""
    try:
        # Aktive Gruppen (Dummy-Wert für jetzt)
        active_groups = 0
        
        # Zahlungen des Users (vereinfacht, ohne addon_id)
        total_payments = db.query(Payment).filter(Payment.user_id == current_user.id).count()
        
        # Tage verbleibend (Dummy-Wert für jetzt)
        days_remaining = 30
        
        # Verfügbare Features (Dummy-Wert für jetzt)
        available_features = 3
        
        return {
            "activeGroups": active_groups,
            "totalPayments": total_payments,
            "daysRemaining": days_remaining,
            "availableFeatures": available_features
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Dashboard-Stats: {e}")
        # Fallback-Werte zurückgeben statt Fehler
        return {
            "activeGroups": 0,
            "totalPayments": 0,
            "daysRemaining": 30,
            "availableFeatures": 3
        }

@router.get("/activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt die neuesten Aktivitäten des Users zurück"""
    try:
        # Dummy-Aktivitäten für jetzt
        activities = [
            {
                "id": 1,
                "type": "login",
                "description": "Erfolgreich eingeloggt",
                "timestamp": datetime.now().isoformat(),
                "icon": "🔐"
            },
            {
                "id": 2,
                "type": "payment",
                "description": "Zahlung erfolgreich",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "icon": "💳"
            }
        ]
        
        return activities
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Aktivitäten: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Laden der Aktivitäten") 