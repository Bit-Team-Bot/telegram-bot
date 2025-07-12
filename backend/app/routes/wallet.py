from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime
from ..database import SessionLocal, get_db
from ..models import Payment
from sqlalchemy.orm import Session
from ..auth import get_current_user
from ..models import User, Package
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["wallet"])

class PaymentWebhook(BaseModel):
    tx_hash: str
    from_address: str
    to_address: str
    amount: float
    token: str
    network: str
    timestamp: datetime

@router.post("/webhook")
def process_webhook(data: PaymentWebhook):
    if data.token.upper() != "USDT" or data.network.upper() != "BEP20":
        raise HTTPException(status_code=400, detail="Nur USDT auf BEP20 erlaubt")

    # Nur Zahlungen an unsere zentrale Wallet akzeptieren (hier Beispiel)
    bot_wallet = "0x123abc456botwallet"  # später dynamisch aus ENV/DB laden
    if data.to_address.lower() != bot_wallet.lower():
        raise HTTPException(status_code=400, detail="Nicht an Bot-Wallet")

    db = SessionLocal()

    existing = db.query(Payment).filter_by(tx_hash=data.tx_hash).first()
    if existing:
        raise HTTPException(status_code=409, detail="Zahlung bereits registriert")

    payment = Payment(
        tx_hash=data.tx_hash,
        from_address=data.from_address,
        to_address=data.to_address,
        amount=data.amount,
        token=data.token,
        network=data.network,
        timestamp=data.timestamp,
        status="empfangen"
    )
    db.add(payment)
    db.commit()

    # Interne Aufteilung vorbereiten (Simulation, Logik kommt später)
    print(f"Verteile {data.amount} USDT auf 60/30/10 Wallets ...")

    return {"success": True, "message": "Zahlung registriert"}

@router.get("/balance")
async def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Wallet-Balance des aktuellen Users abrufen"""
    try:
        # Berechne Gesamtumsatz
        total_spent = db.query(Payment).filter(
            Payment.user_id == current_user.id,
            Payment.status == "completed"
        ).with_entities(func.sum(Payment.amount)).scalar() or 0
        
        # Aktive Pakete (Mock-Daten für jetzt)
        active_packages = db.query(Payment).filter(
            Payment.user_id == current_user.id,
            Payment.status == "completed"
        ).count()
        
        # Verfügbares Guthaben (Mock-Daten für jetzt)
        available_balance = 0.0
        
        return {
            "success": True,
            "balance": {
                "total_spent": float(total_spent),
                "available_balance": available_balance,
                "active_packages": active_packages,
                "currency": "USDT"
            }
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Wallet-Balance: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Balance: {str(e)}")

@router.get("/transactions")
async def get_wallet_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Wallet-Transaktionen des aktuellen Users abrufen"""
    try:
        transactions = db.query(Payment).filter(
            Payment.user_id == current_user.id
        ).order_by(Payment.created_at.desc()).all()
        
        transaction_list = []
        for transaction in transactions:
            transaction_data = {
                "id": transaction.id,
                "type": "payment",
                "amount": transaction.amount,
                "status": transaction.status,
                "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None,
                "tx_hash": transaction.tx_hash,
                "description": f"Paket-Zahlung"
            }
            
            # Paket-Informationen hinzufügen
            if transaction.package_id:
                package = db.query(Package).filter(Package.id == transaction.package_id).first()
                if package:
                    transaction_data["description"] = f"Zahlung für {package.name}"
                    transaction_data["package"] = {
                        "id": package.id,
                        "name": package.name,
                        "price": package.price
                    }
            
            transaction_list.append(transaction_data)
        
        return {
            "success": True,
            "transactions": transaction_list,
            "total_count": len(transaction_list)
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Wallet-Transaktionen: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Transaktionen: {str(e)}")
