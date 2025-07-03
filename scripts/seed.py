import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import SessionLocal, init_db
from backend import models


# Datenbank initialisieren
init_db()
db = SessionLocal()

# Liste der Standardpakete
default_packages = [
    {"name": "Basic", "duration_days": 30, "price_usdt": 10, "signals_allowed": 3},
    {"name": "Pro", "duration_days": 90, "price_usdt": 25, "signals_allowed": 10},
    {"name": "Expert", "duration_days": 180, "price_usdt": 50, "signals_allowed": 25},
    {"name": "Lifetime", "duration_days": 0, "price_usdt": 100, "signals_allowed": 999},
]

# Pakete einfügen (wenn sie nicht existieren)
for p in default_packages:
    existing = db.query(models.Package).filter_by(name=p["name"]).first()
    if not existing:
        package = models.Package(**p)
        db.add(package)

db.commit()
db.close()

print("Pakete erfolgreich eingefügt.")
