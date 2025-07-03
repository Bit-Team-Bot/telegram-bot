from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from app.models import Payment, User, Package
from ..schemas import PaymentResponse, PaymentCreate
from datetime import datetime, timedelta
from typing import List
from ..auth import get_current_user
from ..payments.utils import verify_transaction, create_payment

router = APIRouter(tags=["payments"])

# ----------- PAYMENT ERSTELLEN -----------

@router.post("/", response_model=PaymentResponse)
async def create_payment_endpoint(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Überprüfe Paket
    package = db.query(Package).filter(Package.id == payment.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Paket nicht gefunden")
    
    # Erstelle Zahlung
    db_payment = create_payment(
        user_id=current_user.id,
        package_id=package.id,
        amount=package.price,
        db=db
    )
    
    # Überprüfe Transaktion
    if not verify_transaction(payment.tx_hash, package.price, db):
        raise HTTPException(status_code=400, detail="Ungültige Transaktion")
    
    return db_payment

# ----------- ALLE ZAHLUNGEN ABRUFEN -----------

@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if bool(current_user.is_superadmin):
        return db.query(Payment).all()
    return db.query(Payment).filter(Payment.user_id == current_user.id).all()

# ----------- EINZELNE ZAHLUNG ABRUFEN -----------

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")
    
    if not bool(current_user.is_superadmin) and payment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    return payment

# ----------- ZAHLUNG VERIFIZIEREN -----------

@router.post("/{payment_id}/verify")
async def verify_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not bool(current_user.is_superadmin):
        raise HTTPException(status_code=403, detail="Nur für Administratoren")
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")
    
    if verify_transaction(payment.tx_hash, payment.amount, db):
        return {"status": "success"}
    raise HTTPException(status_code=400, detail="Ungültige Transaktion")

# ----------- ZAHLUNGEN NACH USER -----------

@router.get("/user/{user_id}")
def payments_by_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not bool(current_user.is_superadmin) and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).all()
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "package_name": p.package.name if p.package else "Unbekannt",
            "amount_usdt": p.amount,
            "duration_days": p.package.duration_days if p.package else 0,
            "status": p.status,
            "timestamp": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "ablaufdatum": (
                (p.created_at + timedelta(days=p.package.duration_days)).strftime("%Y-%m-%d")
                if p.package and p.package.duration_days > 0 else "Lifetime"
            )
        })
    return result 

# ----------- AUSSTEHENDE ZAHLUNGEN ABRUFEN -----------

@router.get("/pending", response_model=List[PaymentResponse])
async def get_pending_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Gibt ausstehende Zahlungen für den aktuellen User zurück"""
    if bool(current_user.is_superadmin):
        return db.query(Payment).filter(Payment.status == "pending").all()
    return db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.status == "pending"
    ).all() 