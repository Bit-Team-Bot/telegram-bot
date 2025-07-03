# 📚 Bit-Team-Bot Dokumentation

Willkommen zur vollständigen Dokumentation des Bit-Team-Bot Systems. Hier findest du alle wichtigen Informationen zur Installation, Konfiguration, Entwicklung und Wartung.

## 📁 Dokumentationsstruktur

### 🚀 [Deployment Guide](deployment/)
- **Deployment & QA** - Vollständiger Deployment-Guide
- **Nginx & UFW Setup** - Server-Konfiguration
- **Online Migration** - Migration zu Produktionsumgebung

### 📖 [API Dokumentation](api/)
- **API Endpoints** - Vollständige API-Referenz
- **API Corrections** - Bekannte Probleme und Lösungen
- **Registration Flow** - Benutzerregistrierung und Login

### 🔧 [Development Guide](development/)
- **Module Implementation** - Implementierungsdetails
- **WebApp Initialization** - Frontend-Setup
- **Session Auto Login** - Automatische Anmeldung
- **Pinia Router Fixes** - Frontend-Routing-Lösungen

### 🔧 [Maintenance Guide](maintenance/)
- **Network Error Fix** - Netzwerkprobleme beheben
- **Userbot Automation** - Userbot-Wartung
- **Debug Scripts** - Debugging-Tools und Skripte

## 🚀 Schnellstart

### 1. Installation
```bash
git clone https://github.com/your-repo/telegram-bot.git
cd telegram-bot
```

### 2. Services starten
```bash
# Backend
cd backend && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd webui && npm install
npm run dev

# Userbot Service
cd userbot_service && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py

# Bot
cd bot && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

### 3. Konfiguration
- Kopiere `.env.example` zu `.env` in jedem Modul
- Konfiguriere Telegram API Credentials
- Setze Backend-URLs und Datenbankverbindung

## 🔗 Wichtige Links

- **🌐 Produktions-URLs:**
  - Backend API: `https://api.bit-team-bot.online`
  - Frontend WebUI: `https://webui.bit-team-bot.online`
  - Telegram: `https://t.me`

- **🔧 Development:**
  - Localhost: `http://localhost:8000` (Backend)
  - Localhost: `http://localhost:8080` (Frontend)
  - Userbot Service: `http://localhost:9000`

## 📋 Häufige Aufgaben

### Neuen Service hinzufügen
1. Modul in entsprechendem Verzeichnis erstellen
2. Requirements.txt aktualisieren
3. Environment-Variablen konfigurieren
4. Service in `start_system.py` registrieren

### Debugging
1. Logs in `/var/log/bit-team-bot/` prüfen
2. Debug-Skripte in `docs/maintenance/` verwenden
3. Health-Checks über API-Endpoints

### Deployment
1. SSL-Certificates konfigurieren
2. Environment-Variablen setzen
3. Database-Migration ausführen
4. Services über Systemd starten

## 🆘 Support

Bei Problemen oder Fragen:

1. **Dokumentation durchsuchen** - Oft findest du hier die Lösung
2. **Issues auf GitHub** - Für Bugs und Feature-Requests
3. **Discord Community** - Für schnelle Hilfe
4. **Email Support** - Für komplexe Probleme

## 📝 Dokumentation beitragen

Um die Dokumentation zu verbessern:

1. Fork das Repository
2. Änderungen in einem Feature-Branch
3. Pull Request mit klarer Beschreibung
4. Review und Merge

---

**Letzte Aktualisierung:** Januar 2024  
**Version:** 1.0.0 