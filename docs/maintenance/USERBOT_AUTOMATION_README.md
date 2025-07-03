# 🤖 Automatisierter Userbot-Flow für Cursor

## Übersicht

Dieses System ermöglicht es, Telegram Userbot-Sessions **automatisch über das Webinterface** zu erstellen und zu verwalten, **ohne Terminal-Interaktion**. Der User gibt seine Telefonnummer im Frontend ein, der Code wird automatisch über den Userbot-Service gesendet, und nach Code-Eingabe ist die Session aktiv.

## 🚀 Schnellstart

### 1. Services starten

```bash
# Terminal 1: Backend starten
cd backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

# Terminal 2: Userbot-Service starten
cd userbot_service
source ../venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload --log-level info

# Terminal 3: Frontend starten
cd webui
npm run dev
```

### 2. Automatisierten Flow testen

```bash
# Test-Skript ausführen
cd webui
node test-userbot-flow.js
```

## 📁 Implementierte Dateien

### Frontend (Vue.js)

1. **`webui/src/api/index.js`** - Erweiterte API-Funktionen
   - `userbotAPI.requestCode(phone)` - Code anfordern
   - `userbotAPI.verifyCode(phone, code)` - Code verifizieren
   - `userbotAPI.getSessionStatus()` - Status abrufen
   - `userbotAPI.stopSession()` - Session stoppen

2. **`webui/src/views/Login.vue`** - Erweiterte Login-Komponente
   - Automatische Userbot-Integration
   - Fallback auf Backend bei Fehlern
   - Verbesserte Fehlerbehandlung

3. **`webui/src/components/UserbotSessionManager.vue`** - Session-Management
   - Status-Überwachung
   - Session-Start/Stop
   - Live-Logs
   - Code-Anfrage/Verifizierung

### Test-Skript

4. **`webui/test-userbot-flow.js`** - Vollständiger Test-Suite
   - API-Tests
   - Flow-Simulation
   - Frontend-Integration-Tests

## 🔄 Automatisierter Flow

### Schritt 1: User gibt Telefonnummer ein
```javascript
// Im Frontend (Login.vue)
const userbotResponse = await userbotAPI.requestCode(phone.value);
if (userbotResponse.status === 'code_sent') {
  codeSent.value = true; // Zeige Code-Eingabe-Feld
}
```

### Schritt 2: User gibt Code ein
```javascript
// Im Frontend (Login.vue)
const userbotResponse = await userbotAPI.verifyCode(phone.value, code.value);
if (userbotResponse.status === 'success') {
  // Session ist aktiv, Backend-Login durchführen
  result = await authStore.login(phone.value, code.value);
}
```

### Schritt 3: Session ist aktiv
- Userbot kann Nachrichten senden/empfangen
- Session wird automatisch verwaltet
- Status kann über API abgerufen werden

## 🌐 API-Endpunkte

### Userbot-Service (Port 8001)

| Endpunkt | Methode | Beschreibung |
|----------|---------|--------------|
| `/start` | POST | Code anfordern |
| `/verify` | POST | Code verifizieren |
| `/status` | GET | Status abrufen |
| `/stop` | POST | Session stoppen |

### Beispiel-Requests

```bash
# Code anfordern
curl -X POST http://localhost:8001/start \
  -H "Content-Type: application/json" \
  -d '{"phone": "+49123456789"}'

# Code verifizieren
curl -X POST http://localhost:8001/verify \
  -H "Content-Type: application/json" \
  -d '{"phone": "+49123456789", "code": "123456"}'

# Status abrufen
curl -X GET http://localhost:8001/status
```

## 🎯 Verwendung in Cursor

### 1. Frontend-Integration

Die Login-Komponente ist bereits erweitert. Der User sieht:

1. **Telefonnummer-Eingabe** → Automatische Code-Anfrage über Userbot
2. **Code-Eingabe** → Automatische Verifizierung über Userbot
3. **Erfolgreicher Login** → Session aktiv, Weiterleitung zum Dashboard

### 2. Session-Management

Die `UserbotSessionManager`-Komponente kann in Admin-Bereichen eingebunden werden:

```vue
<template>
  <div>
    <UserbotSessionManager />
  </div>
</template>

<script setup>
import UserbotSessionManager from '@/components/UserbotSessionManager.vue'
</script>
```

### 3. API-Calls im Code

```javascript
// Code anfordern
const result = await userbotAPI.requestCode('+49123456789');

// Code verifizieren
const result = await userbotAPI.verifyCode('+49123456789', '123456');

// Status prüfen
const status = await userbotAPI.getSessionStatus();
```

## 🔧 Konfiguration

### Environment-Variablen

```bash
# userbot_service/.env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BACKEND_URL=https://api.bit-team-bot.online
SERVICE_HOST=0.0.0.0
SERVICE_PORT=8001
```

### Frontend-Konfiguration

```javascript
// webui/src/api/index.js
const USERBOT_API_URL = import.meta.env.VITE_USERBOT_API_URL || 'http://localhost:8001';
```

## 🧪 Testing

### Automatische Tests

```bash
# Test-Suite ausführen
cd webui
node test-userbot-flow.js

# Nur Status-Test
node -e "require('./test-userbot-flow.js').testUserbotStatus()"

# Vollständiger Flow-Test
node -e "require('./test-userbot-flow.js').testCompleteFlow('+49123456789')"
```

### Manuelle Tests

1. **Frontend öffnen**: `http://localhost:8080/login`
2. **Telefonnummer eingeben**: z.B. `+49123456789`
3. **Code eingeben**: Code aus Telegram-App
4. **Login prüfen**: Weiterleitung zum Dashboard

## 🚨 Fehlerbehandlung

### Häufige Fehler

1. **"Userbot-Service nicht erreichbar"**
   - Prüfe ob Userbot-Service läuft (Port 8001)
   - Prüfe Firewall-Einstellungen

2. **"Code-Anfrage fehlgeschlagen"**
   - Zu viele Anfragen (warten)
   - Ungültige Telefonnummer
   - Telegram-API-Limits

3. **"Code-Verifizierung fehlgeschlagen"**
   - Falscher Code
   - Code abgelaufen
   - Session-Timeout

### Fallback-Mechanismus

Das System hat einen automatischen Fallback:
1. **Userbot versuchen** → Bei Fehler
2. **Backend verwenden** → Telegram-Bot-Code senden

## 📊 Monitoring

### Logs überwachen

```bash
# Userbot-Service Logs
tail -f userbot_service/nohup.out

# Backend Logs
tail -f backend/nohup.out

# Frontend Logs (Browser Console)
# Öffne Developer Tools → Console
```

### Status-API

```bash
# Userbot-Status
curl http://localhost:8001/status

# Backend-Status
curl http://localhost:8000/health
```

## 🔄 Deployment

### Produktionsumgebung

1. **Userbot-Service**: Port 8001 (intern)
2. **Backend**: Port 8000 (extern)
3. **Frontend**: Port 8080 (extern)

### Reverse Proxy (nginx)

```nginx
# Userbot-Service (intern)
location /userbot/ {
    proxy_pass http://localhost:8001/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

## 🎉 Fazit

Der automatisierte Userbot-Flow ist jetzt vollständig implementiert:

✅ **Keine Terminal-Interaktion mehr nötig**  
✅ **Automatische Session-Erstellung**  
✅ **Fallback-Mechanismus**  
✅ **Vollständige Frontend-Integration**  
✅ **Monitoring und Logging**  
✅ **Test-Suite verfügbar**  

Der User kann sich jetzt komplett über das Webinterface anmelden, ohne dass manuelle Schritte im Terminal erforderlich sind! 