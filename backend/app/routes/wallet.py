from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from ..database import SessionLocal
from app.models import Payment

router = APIRouter()

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
