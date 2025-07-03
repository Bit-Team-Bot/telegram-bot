# 🤖 Bit-Team-Bot - Telegram Bot Management System

Ein vollständiges Telegram Bot Management System mit WebUI, Backend API und Userbot-Integration.

## 📋 Projektübersicht

Das Bit-Team-Bot System besteht aus mehreren Modulen, die zusammen ein vollständiges Telegram Bot Management System bilden:

### 🌐 **Online-Adressen & IPs**

**Produktions-Domains:**
- `https://api.bit-team-bot.online` - Backend API
- `https://webui.bit-team-bot.online` - Frontend WebUI
- `https://t.me` - Telegram Web Integration
- `https://web.telegram.org` - Telegram Web Integration

**Entwicklungs-IPs:**
- `127.0.0.1` - Localhost (Development)
- `0.0.0.0` - Alle Interfaces
- `192.168.0.96` - SSH Remote Host

**Ports:**
- `8000` - Backend API
- `8080` - Frontend Development
- `9000` - Userbot Service

## 🏗️ **Modul-Architektur**

### 1. **Authentifizierung & Session-Management** (`backend/app/auth/`)
- ✅ User-Login mit Telefonnummer
- ✅ JWT Token Management
- ✅ Session-Überprüfung
- ✅ Logout und Session-Refresh

### 2. **Userbot-Integration** (`userbot_service/`)
- ✅ Telegram-Session-Handling pro Telefonnummer
- ✅ Senden und Prüfen von Login-Codes via Telegram
- ✅ Verknüpfung von WebUI-Login und Userbot-Session
- ✅ Fehlerbehandlung und Session-Verwaltung

### 3. **Userverwaltung** (`backend/app/users/`)
- ✅ Verwaltung der Userdaten, User-IDs (Telegram), Handynummern
- ✅ CRUD-Endpoints (Backend)
- ✅ Datenmodell und User-DB-Anbindung

### 4. **Payments & Pakete** (`backend/app/payments/`)
- ✅ Zahlungsabwicklung (USDT, Stripe, etc.)
- ✅ Abfrage des Zahlungsstatus
- ✅ Buchung und Freischaltung von Paketen
- ✅ Payment-Webhook-Handling

### 5. **Dashboard & WebUI-Komponenten** (`webui/src/components/`)
- ✅ Zentrale UI-Komponente für Paketstatus, Zahlungen, Begrüßung
- ✅ Übersicht aller Funktionen, User-Aktionen, Payment-Status
- ✅ Gruppen-Management UI
- ✅ Einstellungen für User

### 6. **Telegram-Bot-Integration** (`bot/`)
- ✅ Steuerung des Telegram-Bots
- ✅ Verknüpfung von User-IDs, Gruppen, Paketstatus
- ✅ Steuerung von Zugang/Features je nach Paket/Zahlstatus

### 7. **API & Backend** (`backend/`)
- ✅ Zentrale Schnittstelle für alle Module
- ✅ Absicherung aller Endpunkte
- ✅ Fehlerhandling, Logging
- ✅ Saubere REST-Strukturierung

### 8. **Frontend-Store/Session** (`webui/src/store/`)
- ✅ State-Management (Vuex)
- ✅ Synchronisierung von Auth-Status, Payment, Gruppen
- ✅ UI-State Management

### 9. **Dokumentation** (`docs/`)
- ✅ README, Installationsanleitung
- ✅ Modul-Beschreibungen
- ✅ Start-/Deploy-Hinweise

### 10. **Extras & Utilities** (`backend/app/utils/`)
- ✅ Hilfsfunktionen, Fehlerbehandlung
- ✅ Logging, Validierung
- ✅ Sicherheitsfunktionen

## 🚀 **Installation & Setup**

### Voraussetzungen
- Python 3.11+
- Node.js 18+
- PostgreSQL oder SQLite
- Telegram API Credentials

### 1. Repository klonen
```bash
git clone https://github.com/your-repo/telegram-bot.git
cd telegram-bot
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

pip install -r requirements.txt
cp env.example .env
# .env Datei konfigurieren
```

### 3. Frontend Setup
```bash
cd webui
npm install
cp .env.example .env
# .env Datei konfigurieren
```

### 4. Userbot Service Setup
```bash
cd userbot_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Bot Setup
```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# .env Datei konfigurieren
```

## ⚙️ **Konfiguration**

### Environment Variables

**Backend (.env):**
```env
JWT_SECRET=your-super-secret-jwt-key
DATABASE_URL=sqlite:///./telegram_bot.db
CORS_ORIGINS=["https://webui.bit-team-bot.online"]
USERBOT_URL=https://localhost:9000
LOG_LEVEL=INFO
ENVIRONMENT=production
```

**Frontend (.env):**
```env
VITE_API_BASE_URL=https://api.bit-team-bot.online
VITE_APP_TITLE=Bit-Team-Bot
```

**Bot (.env):**
```env
API_ID=your-telegram-api-id
API_HASH=your-telegram-api-hash
BOT_TOKEN=your-bot-token
WEBUI_URL=https://webui.bit-team-bot.online
BACKEND_URL=https://api.bit-team-bot.online
```

## 🏃‍♂️ **Start der Services**

### Development Mode

**Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend:**
```bash
cd webui
npm run dev
```

**Userbot Service:**
```bash
cd userbot_service
source venv/bin/activate
python main.py
```

**Bot:**
```bash
cd bot
source venv/bin/activate
python bot.py
```

### Production Mode

**Mit Docker:**
```bash
docker-compose up -d
```

**Mit Systemd Services:**
```bash
sudo systemctl start telegram-backend
sudo systemctl start telegram-bot
```

## 📊 **API Endpoints**

### Authentication
- `POST /auth/login` - User-Login
- `POST /auth/logout` - User-Logout
- `GET /auth/me` - Aktuelle User-Info
- `POST /auth/refresh` - Token erneuern
- `GET /auth/verify` - Session-Überprüfung

### Users
- `GET /users` - Alle Users (Admin)
- `GET /users/{id}` - User-Details
- `PUT /users/{id}` - User aktualisieren
- `DELETE /users/{id}` - User löschen (Admin)

### Payments
- `POST /payments/create` - Zahlung erstellen
- `GET /payments/history` - Zahlungshistorie
- `GET /payments/pending` - Ausstehende Zahlungen
- `POST /payments/{id}/complete` - Zahlung abschließen
- `POST /payments/{id}/cancel` - Zahlung abbrechen

### Packages
- `GET /packages` - Verfügbare Pakete
- `GET /packages/current` - Aktuelles User-Paket
- `POST /packages/upgrade` - Paket upgraden

### Groups
- `GET /groups` - Alle Gruppen
- `POST /groups` - Gruppe erstellen
- `PUT /groups/{id}` - Gruppe aktualisieren
- `DELETE /groups/{id}` - Gruppe löschen

### Monitoring
- `GET /monitoring/health` - System-Health
- `GET /monitoring/stats` - System-Statistiken
- `GET /monitoring/logs` - System-Logs

## 🔐 **Sicherheit**

### Implementierte Sicherheitsmaßnahmen:
- ✅ JWT Token Authentication
- ✅ Password Hashing mit Salt
- ✅ CORS Protection
- ✅ Rate Limiting
- ✅ Input Validation
- ✅ SQL Injection Protection
- ✅ XSS Protection
- ✅ CSRF Protection

### Security Headers:
```javascript
'X-Content-Type-Options': 'nosniff'
'X-Frame-Options': 'DENY'
'X-XSS-Protection': '1; mode=block'
'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
'Content-Security-Policy': "default-src 'self'"
```

## 📈 **Monitoring & Logging**

### Logging-Konfiguration:
- **Backend:** Structured JSON Logging
- **Frontend:** Console Logging mit Error Tracking
- **Bot:** File-based Logging
- **Userbot:** Session-based Logging

### Monitoring-Endpoints:
- Health Checks
- Performance Metrics
- Error Tracking
- User Activity

## 🧪 **Testing**

### Backend Tests:
```bash
cd backend
pytest tests/
```

### Frontend Tests:
```bash
cd webui
npm run test
```

### E2E Tests:
```bash
npm run test:e2e
```

## 📦 **Deployment**

### Docker Deployment:
```bash
# Build Images
docker build -t bit-team-bot-backend ./backend
docker build -t bit-team-bot-frontend ./webui
docker build -t bit-team-bot-userbot ./userbot_service
docker build -t bit-team-bot-bot ./bot

# Run with Docker Compose
docker-compose up -d
```

### Production Checklist:
- [ ] SSL Certificates konfiguriert
- [ ] Environment Variables gesetzt
- [ ] Database Migration ausgeführt
- [ ] Static Files gebaut
- [ ] Monitoring aktiviert
- [ ] Backup-Strategy implementiert
- [ ] Security Headers konfiguriert
- [ ] Rate Limiting aktiviert

## 📚 **Dokumentation**

Die vollständige Dokumentation findest du im [`docs/`](docs/) Ordner:

- **📖 [API Dokumentation](docs/api/)** - API Endpoints und Integration
- **🚀 [Deployment Guide](docs/deployment/)** - Installation und Deployment
- **🔧 [Development Guide](docs/development/)** - Entwicklung und Debugging
- **🔧 [Maintenance Guide](docs/maintenance/)** - Wartung und Troubleshooting

## 🤝 **Contributing**

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📄 **Lizenz**

Dieses Projekt ist unter der MIT Lizenz lizenziert - siehe [LICENSE](LICENSE) Datei für Details.

## 🆘 **Support**

- **Dokumentation:** [docs/](docs/)
- **Issues:** [GitHub Issues](https://github.com/your-repo/telegram-bot/issues)
- **Discord:** [Bit-Team Discord](https://discord.gg/bit-team)
- **Email:** support@bit-team-bot.online

## 🔄 **Changelog**

### Version 1.0.0 (2024-01-XX)
- ✅ Vollständige Modul-Implementierung
- ✅ Authentifizierung & Session-Management
- ✅ Userbot-Integration
- ✅ Payment-System
- ✅ Dashboard & WebUI
- ✅ API & Backend
- ✅ State-Management
- ✅ Dokumentation

---

**Entwickelt mit ❤️ vom Bit-Team** 