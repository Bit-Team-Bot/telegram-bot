import time
import os
from backend.database import SessionLocal
from backend.models import Payment, PaymentStatus
import requests
from dotenv import load_dotenv

load_dotenv()

# Konfiguration für Blockchain-API
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "")
USDT_CONTRACT = "0x55d398326f99059fF775485246999027B3197955"  # USDT BEP20 auf BSC

def check_usdt_bep20_payment(wallet, amount):
    """
    Prüft über BSCScan API, ob auf der Wallet >= amount USDT eingegangen ist.
    """
    if not BSCSCAN_API_KEY:
        print("[ERROR] BSCScan API Key nicht konfiguriert")
        return False
        
    try:
        url = "https://api.bscscan.com/api"
        params = {
            "module": "account",
            "action": "tokentx",
            "contractaddress": USDT_CONTRACT,
            "address": wallet,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": BSCSCAN_API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "1":
                transactions = data["result"]
                if transactions:
                    # Prüfe die neueste Transaktion
                    latest_tx = transactions[0]
                    tx_amount = float(latest_tx["value"]) / (10 ** 18)  # USDT hat 18 Dezimalstellen
                    if tx_amount >= amount:
                        print(f"[OK] Zahlung gefunden: {tx_amount} USDT an {wallet}")
    return True
                        
        print(f"[INFO] Keine ausreichende Zahlung an {wallet} gefunden")
        return False
        
    except Exception as e:
        print(f"[ERROR] Fehler bei Blockchain-Abfrage: {e}")
        return False

def process_payments():
    db = SessionLocal()
    try:
        pending = db.query(Payment).filter(Payment.status == PaymentStatus.PENDING).all()
        for payment in pending:
            # Hier würde die echte Wallet-Zuordnung erfolgen
            # Für jetzt verwenden wir eine Standard-Wallet
            wallet = os.getenv("PAYMENT_WALLET", "")
            if not wallet:
                print(f"[WARN] Keine Payment-Wallet konfiguriert")
                continue
                
            if check_usdt_bep20_payment(wallet, payment.amount):
                payment.status = PaymentStatus.COMPLETED
                db.commit()
                print(f"[OK] Payment {payment.id} für User {payment.user_id} bestätigt.")
            else:
                print(f"[WAIT] Zahlung für Payment {payment.id} noch nicht eingegangen.")
    finally:
        db.close()

if __name__ == "__main__":
    process_payments()
