from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User
from ..routes.auth import get_current_user
from pydantic import BaseModel
from datetime import datetime
import logging

router = APIRouter(tags=["support"])
logger = logging.getLogger(__name__)

class ContactRequest(BaseModel):
    subject: str
    message: str

class SupportTicket(BaseModel):
    id: int
    user_id: int
    subject: str
    message: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

@router.post("/contact")
async def submit_contact_form(
    contact_data: ContactRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sendet eine Support-Anfrage"""
    try:
        # Hier würde die Logik zum Speichern der Support-Anfrage implementiert werden
        # Für jetzt geben wir nur eine Bestätigung zurück
        
        logger.info(f"📧 Support-Anfrage von User {current_user.id}: {contact_data.subject}")
        
        return {
            "success": True,
            "message": "Ihre Nachricht wurde erfolgreich gesendet. Wir werden uns schnellstmöglich bei Ihnen melden.",
            "ticket_id": f"TICKET-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        }
    except Exception as e:
        logger.error(f"❌ Fehler beim Senden der Support-Anfrage: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Senden der Nachricht: {str(e)}")

@router.get("/tickets")
async def get_user_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Gibt alle Support-Tickets des Users zurück"""
    try:
        # Hier würden die Support-Tickets aus der DB geladen werden
        # Für jetzt geben wir Mock-Daten zurück
        tickets = [
            {
                "id": 1,
                "subject": "Frage zu Paket-Upgrade",
                "status": "open",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T14:20:00Z"
            },
            {
                "id": 2,
                "subject": "Technisches Problem",
                "status": "closed",
                "created_at": "2024-01-10T09:15:00Z",
                "updated_at": "2024-01-12T16:45:00Z"
            }
        ]
        
        return tickets
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Support-Tickets: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Tickets: {str(e)}")

@router.get("/faq")
async def get_faq():
    """Gibt häufig gestellte Fragen zurück"""
    try:
        faqs = [
            {
                "question": "Wie kann ich mein Paket upgraden?",
                "answer": "Sie können Ihr Paket über die Pakete-Seite upgraden. Wählen Sie das gewünschte Paket aus und folgen Sie den Anweisungen zur Zahlung."
            },
            {
                "question": "Wie funktioniert die Zahlung?",
                "answer": "Wir akzeptieren verschiedene Kryptowährungen. Nach der Zahlung wird Ihr Konto automatisch freigeschaltet."
            },
            {
                "question": "Kann ich mein Konto löschen?",
                "answer": "Ja, Sie können Ihr Konto in den Einstellungen löschen. Beachten Sie, dass diese Aktion nicht rückgängig gemacht werden kann."
            },
            {
                "question": "Wie lange dauert die Aktivierung?",
                "answer": "Nach erfolgreicher Zahlung wird Ihr Konto innerhalb von 10-30 Minuten aktiviert."
            },
            {
                "question": "Was passiert bei technischen Problemen?",
                "answer": "Bei technischen Problemen kontaktieren Sie uns bitte über den Support. Wir werden das Problem schnellstmöglich beheben."
            }
        ]
        
        return faqs
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der FAQ: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der FAQ: {str(e)}")

@router.get("/contact-info")
async def get_contact_info():
    """Gibt Kontaktinformationen zurück"""
    try:
        contact_info = {
            "email": "support@bit-team-bot.online",
            "telegram": "@bit_team_support",
            "whatsapp": "+49 123 456789",
            "response_time": "24 Stunden",
            "business_hours": "Mo-Fr 9:00-18:00 Uhr"
        }
        
        return contact_info
    except Exception as e:
        logger.error(f"❌ Fehler beim Abrufen der Kontaktinformationen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Kontaktinformationen: {str(e)}") 