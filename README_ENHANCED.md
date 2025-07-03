# Telegram Bot System - Erweiterte Dokumentation

## Übersicht

Das Telegram Bot System ist eine umfassende Plattform für Gruppenverwaltung, Userbot-Management und Signalgruppen-Handling. Das System besteht aus mehreren Komponenten, die nahtlos zusammenarbeiten.

## Systemarchitektur

```
telegram-bot/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── models.py       # Datenbankmodelle
│   │   ├── routes/         # API-Endpunkte
│   │   ├── tasks/          # Hintergrundaufgaben
│   │   └── utils/          # Hilfsfunktionen
├── bot/                    # Telegram Bot (Pyrogram)
│   ├── handlers/           # Bot-Handler
│   └── menus/              # Bot-Menüs
├── userbot_service/        # Userbot-Management
├── frontend/               # Web-Interface
└── webui/                  # Alternative UI
```

## Wichtige Verbesserungen

### 1. Userbot-Integration

**Automatische Session-Verwaltung:**
- Nach erfolgreicher Paketbuchung wird automatisch eine Userbot-Session angelegt
- Bei Zahlungsbestätigung/Verlängerung werden Sessions reaktiviert
- Nach 2 Wochen ohne Zahlung werden Sessions automatisch gelöscht

**Implementierung:**
```python
# backend/app/payments/enhanced_payment_handler.py
def activate_package_after_payment(self, payment_id: int, db: Session):
    # Paket aktivieren
    # Userbot-Session erstellen
    # Signalgruppen freischalten
    # Gruppen erstellen
```

### 2. Gruppenverwaltung

**Automatische Abhängigkeiten-Verwaltung:**
- Beim Erstellen/Löschen einer Gruppe werden alle abhängigen Daten automatisch angelegt/gelöscht
- Änderungen an Gruppeneinstellungen werden immer in die Datenbank geschrieben

**Implementierung:**
```python
# backend/app/routes/enhanced_group_management.py
def create_group_with_dependencies(self, group_data: Dict, owner_id: int, db: Session):
    # Gruppe erstellen
    # Besitzer als Admin hinzufügen
    # Standard-Einstellungen anwenden

def delete_group_with_dependencies(self, group_id: int, db: Session):
    # Alle User-Rollen löschen
    # Alle Warnungen löschen
    # Alle Mutes löschen
    # Alle geplanten Nachrichten löschen
    # Gruppe selbst löschen
```

### 3. Signalgruppen/Abonnements

**Automatische Verwaltung:**
- Bei Abo-Buchung/Verlängerung werden Signalgruppen und Subscriptions aktualisiert
- Beim Löschen von Signalgruppen werden alle abhängigen Daten mitgelöscht

### 4. Payment-Workflow

**Sofortige Freischaltung:**
- Nach Zahlungsbestätigung werden alle gekauften Module sofort freigeschaltet
- Userbot, Addons, Gruppen, Signalgruppen, Features werden automatisch aktiviert

### 5. Aufräum- und Cleanup-Jobs

**Umfassendes Cleanup-System:**
```python
# backend/app/tasks/comprehensive_cleanup.py
class ComprehensiveCleanup:
    def cleanup_expired_packages(self, db: Session)
    def cleanup_expired_userbot_sessions(self, db: Session)
    def cleanup_expired_signal_groups(self, db: Session)
    def cleanup_orphaned_data(self, db: Session)
```

**Tägliche Cleanup-Routine:**
- Löscht abgelaufene Pakete und alle abhängigen Daten
- Löscht abgelaufene Userbot-Sessions und Session-Dateien
- Löscht abgelaufene Signalgruppen-Abonnements
- Löscht verwaiste Daten ohne Referenzen

### 6. Error-Handling und Logging

**Erweitertes Error-Handling:**
```python
# backend/app/utils/enhanced_error_handling.py
class EnhancedErrorHandler:
    def log_error(self, error: Exception, context: Dict, user_id: int)
    def handle_database_error(self, error: SQLAlchemyError, operation: str)
    def handle_api_error(self, error: Exception, endpoint: str)
    def handle_userbot_error(self, error: Exception, session_id: int)
    def handle_payment_error(self, error: Exception, payment_id: int)
```

**Features:**
- Detailliertes Logging aller Fehler mit Kontext
- Spezifische Behandlung verschiedener Fehlertypen
- Automatische Benachrichtigung bei kritischen Fehlern
- Request/Response-Logging für Debugging

## API-Endpunkte

### Authentifizierung
- `POST /auth/login` - User-Login
- `POST /auth/logout` - User-Logout
- `GET /auth/me` - Aktueller User

### Pakete
- `GET /user/packages/available` - Verfügbare Pakete
- `GET /user/packages/current` - Aktuelles Paket
- `POST /user/packages/addons/{addon_id}/book` - Add-on buchen

### Zahlungen
- `POST /payments/` - Zahlung erstellen
- `GET /payments/` - Alle Zahlungen
- `POST /payments/{payment_id}/verify` - Zahlung verifizieren

### Gruppenverwaltung
- `POST /admin/groups/` - Gruppe erstellen
- `DELETE /admin/groups/{group_id}` - Gruppe löschen
- `PUT /admin/groups/{group_id}/settings` - Einstellungen aktualisieren

### Userbot-Management
- `POST /userbot/sessions/` - Session erstellen
- `GET /userbot/sessions/` - Alle Sessions
- `DELETE /userbot/sessions/{session_id}` - Session löschen

### Signalgruppen
- `GET /signalgroups/` - Alle Signalgruppen
- `POST /signalgroups/{group_id}/subscribe` - Abonnieren
- `DELETE /signalgroups/{group_id}/unsubscribe` - Kündigen

## Datenbankmodelle

### Wichtige Tabellen
- `users` - Benutzer
- `packages` - Pakete
- `userbot_sessions` - Userbot-Sessions
- `groups` - Gruppen
- `group_user_roles` - Gruppen-Rollen
- `signal_groups` - Signalgruppen
- `signal_group_subscriptions` - Signalgruppen-Abonnements

### Beziehungen
- User → Packages (1:n)
- User → UserbotSessions (1:n)
- User → Groups (n:n über GroupUserRole)
- SignalGroup → SignalGroupSubscription (1:n)

## Bot-Funktionen

### Admin-Menü
- Mitglieder verwalten
- Begrüßungstext einstellen
- Nachtmodus konfigurieren
- Weiterleitungen erlauben/verbieten
- Tägliche Info-Einstellungen
- Rechte/Rollen verwalten
- Beleidigungen verbieten
- Links erlauben/verbieten

### User-Management
- User muten
- User verwarnen
- User kicken
- Rollen zuweisen

## Installation und Setup

### Voraussetzungen
- Python 3.8+
- PostgreSQL oder SQLite
- Telegram API Credentials
- Node.js (für Frontend)

### Installation
```bash
# Backend
cd backend
pip install -r requirements.txt
python run.py

# Bot
cd bot
pip install -r requirements.txt
python bot.py

# Userbot-Service
cd userbot_service
pip install -r requirements.txt
python main.py

# Frontend
cd frontend
npm install
npm start
```

### Umgebungsvariablen
```bash
# Backend
DATABASE_URL=sqlite:///telegram_bot.db
SECRET_KEY=your-secret-key
API_ID=your-telegram-api-id
API_HASH=your-telegram-api-hash

# Bot
BOT_TOKEN=your-bot-token
BACKEND_URL=http://localhost:8000

# Userbot-Service
API_ID=your-telegram-api-id
API_HASH=your-telegram-api-hash
```

## Monitoring und Wartung

### Tägliche Cleanup-Routine
```python
from backend.app.tasks.comprehensive_cleanup import run_daily_comprehensive_cleanup

# Täglich ausführen
results = run_daily_comprehensive_cleanup()
```

### Log-Dateien
- `backend_debug.log` - Backend-Logs
- `bot.log` - Bot-Logs
- `webui_debug.log` - Frontend-Logs

### Error-Monitoring
- Alle Fehler werden in `backend_debug.log` protokolliert
- Kritische Fehler werden automatisch an Monitoring-Service gesendet
- Request/Response-Logging für Performance-Monitoring

## Sicherheit

### Authentifizierung
- JWT-basierte Authentifizierung
- Session-Management mit Ablaufzeiten
- Rollenbasierte Zugriffskontrolle

### Datenbank
- Prepared Statements gegen SQL-Injection
- Input-Validierung
- CASCADE-Delete für referentielle Integrität

### API-Sicherheit
- Rate Limiting
- Input-Sanitization
- CORS-Konfiguration

## Troubleshooting

### Häufige Probleme

1. **"Ungültige Callback-Daten" im Bot**
   - Callback-Handler Regex überprüfen
   - Callback-Daten-Struktur konsistent halten

2. **Userbot-Sessions funktionieren nicht**
   - Session-Dateien überprüfen
   - API-Credentials validieren
   - Userbot-Service-Logs prüfen

3. **Datenbankfehler**
   - Verbindung zur Datenbank prüfen
   - Migrationen ausführen
   - Logs auf spezifische Fehler prüfen

### Debug-Modus
```bash
# Backend im Debug-Modus starten
cd backend
python run.py --debug

# Bot im Debug-Modus starten
cd bot
python bot.py --debug
```

## Entwicklung

### Code-Struktur
- Modularer Aufbau
- Dependency Injection
- Error-Handling auf allen Ebenen
- Umfassendes Logging

### Testing
```bash
# Backend-Tests
cd backend
python -m pytest tests/

# Bot-Tests
cd bot
python -m pytest tests/
```

### Deployment
- Docker-Container für alle Services
- Nginx als Reverse Proxy
- SSL/TLS-Verschlüsselung
- Automatische Backups

## Support

Bei Problemen oder Fragen:
1. Logs überprüfen
2. Error-Handling-System nutzen
3. Dokumentation konsultieren
4. GitHub Issues erstellen

## Changelog

### Version 2.0 (Aktuell)
- Umfassendes Cleanup-System
- Erweiterte Gruppenverwaltung
- Verbessertes Error-Handling
- Automatische Userbot-Integration
- Vollständige Payment-Integration 