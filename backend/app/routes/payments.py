from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Payment, User, Package
from ..schemas import PaymentResponse, PaymentCreate
from typing import List
from ..auth import get_current_user
from ..payments.utils import verify_transaction, create_payment
from datetime import datetime, timedelta
import logging

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
async def get_user_payments(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zahlungen eines Users abrufen"""
    if current_user.id != user_id and not current_user.is_superadmin:
        raise HTTPException(status_code=403, detail="Keine Berechtigung")
    
    payments = db.query(Payment).filter(Payment.user_id == user_id).all()
    return payments

# ===== FEHLENDER PAYMENTS ENDPUNKT =====

@router.get("/history")
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zahlungshistorie des aktuellen Users abrufen"""
    try:
        payments = db.query(Payment).filter(
            Payment.user_id == current_user.id
        ).order_by(Payment.created_at.desc()).all()
        
        payment_history = []
        for payment in payments:
            payment_data = {
                "id": payment.id,
                "amount": payment.amount,
                "status": payment.status,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "completed_at": payment.completed_at.isoformat() if payment.completed_at else None,
                "tx_hash": payment.tx_hash
            }
            
            # Paket-Informationen hinzufügen
            if payment.package_id:
                package = db.query(Package).filter(Package.id == payment.package_id).first()
                if package:
                    payment_data["package"] = {
                        "id": package.id,
                        "name": package.name,
                        "price": package.price
                    }
            
            payment_history.append(payment_data)
        
        return {
            "success": True,
            "payments": payment_history,
            "total_count": len(payment_history)
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Zahlungshistorie: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Zahlungshistorie: {str(e)}") 