from app.models import Payment
from sqlalchemy.orm import Session
from datetime import datetime

def verify_transaction(tx_hash: str, amount: float, db: Session) -> bool:
    """
    Dummy-Implementierung: Überprüft, ob eine Transaktion mit dem Hash existiert und den richtigen Betrag hat.
    In einer echten Implementierung sollte hier die Blockchain/API-Abfrage erfolgen.
    """
    payment = db.query(Payment).filter(Payment.tx_hash == tx_hash, Payment.amount == amount).first()
    return payment is not None


def create_payment(user_id: int, package_id: int, amount: float, db: Session) -> Payment:
    """
    Legt eine neue Zahlung in der Datenbank an.
    """
    payment = Payment(
        user_id=user_id,
        package_id=package_id,
        amount=amount,
        status="pending",
        created_at=datetime.utcnow()
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment 