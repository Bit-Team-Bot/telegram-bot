# Telegram Bot System - Vollständige Dokumentation

## 📋 Übersicht

Dieses System besteht aus einem umfassenden Telegram-Bot mit Backend-API, Userbot-Funktionalität, WebUI und Datenbank-Integration. Das System bietet Signal-Gruppen-Management, Zahlungsabwicklung, Userbot-Sessions und ein modernes Dashboard.

## 🏗️ Systemarchitektur

```
telegram-bot/
├── backend/           # FastAPI Backend
├── userbot/          # Telegram Userbot
├── webui/            # React WebUI
├── bot/              # Telegram Bot
├── database/         # SQLite Datenbank
└── docs/            # Dokumentation
```

## 🚀 Schnellstart

### Voraussetzungen

- Python 3.8+
- Node.js 16+
- SQLite3
- Telegram Bot Token
- Telegram API Credentials

### Installation

1. **Repository klonen**
```bash
git clone <repository-url>
cd telegram-bot
```

2. **Umgebungsvariablen konfigurieren**
```bash
cp .env.example .env
# .env-Datei mit Ihren Werten bearbeiten
```

3. **Backend starten**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

4. **WebUI starten**
```bash
cd webui
npm install
npm run dev
```

5. **Bot starten**
```bash
cd bot
python main.py
```

6. **Userbot starten**
```bash
cd userbot
python main.py
```

## ⚙️ Konfiguration

### .env-Datei

```env
# Server-Konfiguration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Datenbank
DATABASE_URL=sqlite:///./telegram_bot.db

# JWT
JWT_SECRET=your-secret-key
ALGORITHM=HS256

# Telegram
BOT_TOKEN=your-bot-token
USERBOT_URL=http://localhost:8001

# WebUI
WEBUI_URL=http://localhost:3000

# Logging
LOG_LEVEL=INFO
```

## 📊 Datenmodelle

### User Management
- **User**: Zentrale Benutzerentität mit Telegram-Integration
- **UserSession**: Session-Management für WebUI
- **UserbotSession**: Userbot-Session-Verwaltung

### Paket-System
- **PackageTemplate**: Vorlagen für Pakete (Basic, Advanced, Pro, Lifetime)
- **Package**: Benutzer-spezifische Pakete
- **Addon**: Zusätzliche Features
- **AddonTier**: Verschiedene Stufen für Addons
- **PackageAddon**: Verknüpfung zwischen Paketen und Addons
- **UserAddon**: Benutzer-spezifische Addons

### Zahlungssystem
- **Payment**: Zahlungsverwaltung
- **Wallet**: Wallet-Funktionalität

### Gruppen-Management
- **Group**: Telegram-Gruppen
- **GroupMember**: Gruppenmitglieder
- **GroupWarning**: Verwarnungen
- **GroupMute**: Stummschaltungen
- **GroupKick**: Ausschlüsse

## 🔐 Authentifizierung

### Telegram-Login
1. User sendet Telegram-ID an `/auth/telegram-login`
2. System generiert Login-Code
3. User gibt Code in WebUI ein
4. JWT-Token wird erstellt

### Session-Management
- Automatische Token-Erneuerung
- Session-Timeout nach 24 Stunden
- Sichere Logout-Funktionalität

## 💰 Zahlungssystem

### Paket-Kauf
1. User wählt Paket im WebUI
2. Zahlungsanfrage wird erstellt
3. User führt Zahlung durch
4. Paket wird automatisch aktiviert
5. Userbot-Session wird gestartet

### Zahlungsstatus
- `PENDING`: Zahlung ausstehend
- `COMPLETED`: Zahlung erfolgreich
- `FAILED`: Zahlung fehlgeschlagen
- `REFUNDED`: Zahlung erstattet

## 🤖 Userbot-Funktionalität

### Session-Management
- Automatischer Start nach Paketkauf
- Session-Monitoring
- Automatische Beendigung bei Paket-Ablauf

### Gruppen-Integration
- Automatischer Beitritt zu Signal-Gruppen
- Nachrichten-Monitoring
- Verwarnungs-System

## 📱 WebUI Features

### Dashboard
- 4 Hauptkacheln: Aktive Gruppen, Zahlungen, Verbleibende Tage, Verfügbare Features
- Paket-Panel mit aktiven Paketen
- Ladeindikatoren und Fehlerbehandlung

### Paket-Verwaltung
- Übersicht aller verfügbaren Pakete
- Kauf-Funktionalität
- Paket-Details und Features

### Admin-Bereich
- User-Management
- Paket-Verwaltung
- Zahlungsübersicht
- System-Monitoring

## 🔧 Backend-API

### Haupt-Endpoints

#### Authentifizierung
- `POST /auth/telegram-login` - Telegram-Login
- `POST /auth/verify-code` - Code-Verifikation
- `POST /auth/logout` - Logout

#### User-Management
- `POST /users/register_or_update` - User-Registrierung
- `POST /users/link_phone` - Telefonnummer verknüpfen
- `GET /users/profile` - User-Profil

#### Paket-System
- `GET /packages/` - Alle Pakete
- `POST /packages/purchase` - Paket kaufen
- `GET /user_packages/active` - Aktive Pakete

#### Zahlungen
- `POST /payments/create` - Zahlung erstellen
- `GET /payments/history` - Zahlungshistorie
- `POST /payments/verify` - Zahlung verifizieren

#### Userbot
- `POST /userbot/start_session` - Session starten
- `GET /userbot/sessions` - Aktive Sessions
- `POST /userbot/stop_session` - Session beenden

#### Monitoring
- `GET /monitoring/stats` - System-Statistiken
- `GET /monitoring/performance` - Performance-Metriken
- `GET /monitoring/errors` - Fehler-Logs

## 🛡️ Sicherheit

### Datenbank-Sicherheit
- Foreign Keys mit `ondelete="CASCADE"`
- Relationships mit `cascade="all, delete"`
- Automatische Datenleichen-Bereinigung

### API-Sicherheit
- JWT-Token-Authentifizierung
- Rate-Limiting
- Input-Validierung
- SQL-Injection-Schutz

### Error-Handling
- Umfassendes Error-Logging
- Strukturierte Fehlerantworten
- Monitoring-Integration

## 📈 Monitoring & Logging

### Performance-Monitoring
- API-Response-Zeiten
- Datenbank-Performance
- System-Ressourcen

### Error-Monitoring
- Automatische Fehler-Erkennung
- Kritische Fehler-Benachrichtigung
- Error-Trend-Analyse

### Logging
- Strukturiertes Logging
- Verschiedene Log-Level
- Log-Rotation

## 🧪 Testing

### API-Tests
```bash
cd backend
pytest tests/test_api.py -v
```

### Test-Coverage
- Unit-Tests für alle Module
- Integration-Tests für API-Endpoints
- End-to-End-Tests für kritische Workflows

## 🚀 Deployment

### Systemd-Services

#### Backend Service
```ini
[Unit]
Description=Telegram Bot Backend
After=network.target

[Service]
Type=simple
User=manny
WorkingDirectory=/home/manny/telegram-bot/backend
Environment=PATH=/home/manny/telegram-bot/backend/venv/bin
ExecStart=/home/manny/telegram-bot/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Bot Service
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=manny
WorkingDirectory=/home/manny/telegram-bot/bot
Environment=PATH=/home/manny/telegram-bot/bot/venv/bin
ExecStart=/home/manny/telegram-bot/bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Userbot Service
```ini
[Unit]
Description=Telegram Userbot
After=network.target

[Service]
Type=simple
User=manny
WorkingDirectory=/home/manny/telegram-bot/userbot
Environment=PATH=/home/manny/telegram-bot/userbot/venv/bin
ExecStart=/home/manny/telegram-bot/userbot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx-Konfiguration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # WebUI
    location / {
        root /home/manny/telegram-bot/webui/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Wartung

### Datenbank-Migrationen
```bash
cd backend
alembic upgrade head
```

### Log-Rotation
```bash
# Automatische Log-Rotation konfigurieren
sudo logrotate /etc/logrotate.d/telegram-bot
```

### Backup-Strategie
```bash
# Tägliches Backup
0 2 * * * /home/manny/telegram-bot/scripts/backup.sh
```

## 🐛 Troubleshooting

### Häufige Probleme

#### Backend startet nicht
```bash
# Logs prüfen
sudo journalctl -u telegram-bot-backend -f

# Port-Konflikte prüfen
sudo netstat -tlnp | grep :8000
```

#### Userbot-Sessions funktionieren nicht
```bash
# Session-Logs prüfen
tail -f /home/manny/telegram-bot/userbot/logs/userbot.log

# API-Verbindung testen
curl http://localhost:8000/userbot/sessions
```

#### WebUI lädt nicht
```bash
# Build-Status prüfen
cd webui
npm run build

# Nginx-Logs prüfen
sudo tail -f /var/log/nginx/error.log
```

## 📞 Support

### Logs finden
- Backend: `/home/manny/telegram-bot/backend/logs/`
- Bot: `/home/manny/telegram-bot/bot/logs/`
- Userbot: `/home/manny/telegram-bot/userbot/logs/`
- System: `sudo journalctl -u telegram-bot-*`

### Monitoring-Dashboard
- URL: `http://your-domain.com/monitoring`
- Performance-Metriken
- Error-Logs
- System-Status

## 🔄 Updates

### Automatische Updates
```bash
# Update-Script ausführen
./scripts/update.sh
```

### Manuelle Updates
```bash
# Code aktualisieren
git pull origin main

# Dependencies aktualisieren
cd backend && pip install -r requirements.txt
cd ../webui && npm install

# Services neu starten
sudo systemctl restart telegram-bot-*
```

## 📝 Changelog

### Version 1.0.0
- ✅ Vollständiges Backend-System
- ✅ Userbot-Integration
- ✅ WebUI mit Dashboard
- ✅ Zahlungssystem
- ✅ Monitoring & Logging
- ✅ Umfassende Tests
- ✅ Deployment-Konfiguration

## 📄 Lizenz

Dieses Projekt ist proprietär und nicht zur öffentlichen Nutzung bestimmt.

---

**Entwickelt für professionelle Telegram-Bot-Lösungen mit umfassender Funktionalität und robuster Architektur.** 