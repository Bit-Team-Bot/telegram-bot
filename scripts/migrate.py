from backend.database import Base, engine
from backend import models

print("Datenbankstruktur wird erstellt ...")
Base.metadata.create_all(bind=engine)
print("Migration abgeschlossen.")