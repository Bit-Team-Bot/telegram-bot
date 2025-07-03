# 🔧 Debug-Skripte Dokumentation

Diese Dokumentation beschreibt die Debug-Start-Skripte für das Bit-Team-Bot System.

## 📋 Übersicht

Die Debug-Skripte sind speziell für die Entwicklung und Fehlerbehebung konzipiert und bieten:

- **Vollständiges Logging** - Alle Services loggen detailliert
- **Externe Erreichbarkeit** - Services sind von außen erreichbar
- **Automatische Virtual Environment Aktivierung** - Jeder Service verwendet sein eigenes venv
- **PID-Management** - Sauberes Starten/Stoppen der Services
- **Netzwerk-Tests** - Automatische Erreichbarkeitstests

## 🚀 Verfügbare Debug-Skripte

### 1. **start_all_services_debug.sh** - Komplett-Debug
Startet alle Services (Backend, Bot, WebUI) gleichzeitig im Debug-Modus.

```bash
./start_all_services_debug.sh
```

**Features:**
- Startet Backend mit eigenem venv aus `backend/`
- Startet Bot mit eigenem venv aus `bot/`
- Überwacht WebUI-Status
- Automatische Service-Tests
- Zentrale Log-Dateien

### 2. **start_backend_debug.sh** - Backend-Debug
Startet nur das Backend im Debug-Modus.

```bash
./start_backend_debug.sh
```

**Features:**
- Verwendet venv aus `backend/venv/`
- Vollständiges uvicorn Debug-Logging
- Externe Erreichbarkeit (0.0.0.0:8000)
- Automatische Dependency-Prüfung
- Health-Check Integration

### 3. **start_bot_debug.sh** - Bot-Debug
Startet nur den Telegram Bot im Debug-Modus.

```bash
./start_bot_debug.sh
```

**Features:**
- Verwendet venv aus `bot/venv/`
- Pyrogram Debug-Logging
- Session-Management
- Backend-Connectivity-Tests
- Umgebungsvariablen-Validierung

### 4. **start_webui_debug.sh** - WebUI-Debug
Überwacht die WebUI und Nginx-Logs.

```bash
./start_webui_debug.sh
```

**Features:**
- Nginx-Status-Überwachung
- Live-Log-Monitoring
- Netzwerk-Erreichbarkeitstests
- Performance-Monitoring

## 🔧 Virtual Environment Management

### Wichtige Änderung (2024)
**Alle Debug-Skripte verwenden jetzt die Virtual Environments aus den jeweiligen Service-Verzeichnissen:**

- **Backend:** `backend/venv/`
- **Bot:** `bot/venv/`
- **Userbot Service:** `userbot_service/venv/`

### Automatische venv-Erstellung
Falls ein venv nicht existiert, wird es automatisch erstellt:

```bash
# Backend venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Bot venv
cd bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Log-Dateien

### Debug-Log-Dateien
- `backend_debug.log` - Backend Debug-Logs
- `bot_debug.log` - Bot Debug-Logs
- `webui_debug.log` - WebUI Debug-Logs

### PID-Dateien
- `.backend_debug.pid` - Backend Prozess-ID
- `.bot_debug.pid` - Bot Prozess-ID

## 🌐 Netzwerk-Konfiguration

### Automatische IP-Erkennung
Die Skripte erkennen automatisch die externe IP-Adresse:

```bash
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unbekannt")
```

### Konfigurierte URLs
- **Backend:** `http://$EXTERNAL_IP:8000`
- **WebUI:** `http://$EXTERNAL_IP`
- **API Docs:** `http://$EXTERNAL_IP:8000/docs`
- **Health Check:** `http://$EXTERNAL_IP:8000/health`

## 🔍 Debug-Features

### Backend Debug
- **Log-Level:** `debug`
- **Access-Log:** Aktiviert
- **Reload:** Aktiviert
- **Proxy-Headers:** Unterstützt
- **Forwarded-IPs:** Alle erlaubt

### Bot Debug
- **Pyrogram Log-Level:** `DEBUG`
- **Python Unbuffered:** Aktiviert
- **Session-Tracking:** Aktiviert
- **Backend-Connectivity:** Getestet

### WebUI Debug
- **Nginx-Status:** Überwacht
- **Live-Logs:** Echtzeit
- **Erreichbarkeitstests:** Lokal/Extern/Domain
- **Performance-Monitoring:** Aktiviert

## 🛠️ Troubleshooting

### Häufige Probleme

#### 1. Virtual Environment nicht gefunden
```bash
# Lösung: venv manuell erstellen
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Port bereits belegt
```bash
# Lösung: Prozess beenden
sudo lsof -ti:8000 | xargs kill -9
```

#### 3. Firewall blockiert
```bash
# Lösung: Ports freigeben
sudo ufw allow 8000  # Backend
sudo ufw allow 8080  # WebUI
```

#### 4. Services nicht erreichbar
```bash
# Lösung: Netzwerk-Test
curl -v http://localhost:8000/health
curl -v http://localhost
```

## 📝 Verwendung

### 1. Einzelne Services debuggen
```bash
# Nur Backend
./start_backend_debug.sh

# Nur Bot
./start_bot_debug.sh

# Nur WebUI
./start_webui_debug.sh
```

### 2. Alle Services gleichzeitig
   ```bash
   ./start_all_services_debug.sh
   ```

### 3. Services beenden
```bash
# Ctrl+C in den jeweiligen Terminals
# Oder PID-Dateien löschen
rm -f .backend_debug.pid .bot_debug.pid
```

## 🔒 Sicherheitshinweise

### Debug-Modus
- **Nur für Entwicklung** verwenden
- **Nicht in Produktion** einsetzen
- **Firewall-Regeln** beachten
- **Sensible Daten** in Logs vermeiden

### Externe Erreichbarkeit
- **Port 8000** für Backend
- **Port 80/443** für WebUI
- **Firewall-Konfiguration** prüfen
- **SSL/TLS** in Produktion verwenden

## 📚 Weitere Dokumentation

- **API Dokumentation:** [docs/api/](docs/api/)
- **Deployment Guide:** [docs/deployment/](docs/deployment/)
- **Development Guide:** [docs/development/](docs/development/)

---

**Letzte Aktualisierung:** Januar 2024  
**Version:** 2.0.0 (Virtual Environment Update) 