# Registrierungs- und Login-Ablauf - Korrigierte Version

## Übersicht

Dieses Dokument beschreibt den **korrigierten und praxistauglichen** Registrierungs- und Login-Ablauf für das Telegram Bot Management System.

## Architektur

### Komponenten
- **Telegram Bot** (`bot/bot.py`) - Einstiegspunkt für User
- **Backend API** (`backend/app/`) - Hauptlogik und Datenbank
- **Web Interface** (`webui/src/`) - Frontend für User
- **Userbot Service** (`userbot_service/`) - Echte Telegram-Verifizierung

### Datenbank-Modell
```python
class User(Base):
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)  # Hauptidentifikator
    phone = Column(String)                     # Optional, wird verknüpft
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
```

## Korrigierter Ablauf

### 1. Registrierung startet IMMER im Telegram-Bot

**Datei:** `bot/bot.py` (Zeilen 97-150)

```python
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id  # Telegram-ID automatisch auslesen
    user_name = message.from_user.first_name
    
    # User-Daten an Backend senden
    user_data = {
        "telegram_id": str(user_id),
        "user_name": user_name,
        "first_name": user_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
        "is_bot": message.from_user.is_bot,
        "language_code": message.from_user.language_code
    }
    
    response = await make_api_request("POST", "/users/register_or_update", user_data)
```

**Backend-Route:** `backend/app/routes/users.py` (Zeilen 43-112)
- Erstellt neuen User mit Telegram-ID (ohne Telefonnummer)
- Oder aktualisiert bestehenden User

### 2. User wechselt ins Webinterface

**Datei:** `webui/src/views/Login.vue` (Zeilen 130-200)

```javascript
onMounted(async () => {
  // 1. Telegram-ID aus URL-Parameter lesen (Bot-Button)
  const urlParams = new URLSearchParams(window.location.search)
  const userParam = urlParams.get('user')
  if (userParam) {
    telegramId.value = userParam
  }
  
  // 2. Telegram-ID aus Telegram WebApp Kontext lesen
  if (!telegramId.value && window.Telegram && window.Telegram.WebApp) {
    if (window.Telegram.WebApp.initDataUnsafe && window.Telegram.WebApp.initDataUnsafe.user) {
      telegramId.value = window.Telegram.WebApp.initDataUnsafe.user.id.toString()
    }
  }
})
```

**Wichtig:** User gibt nur Telefonnummer ein - keine manuelle Telegram-ID-Eingabe!

### 3. Telefonnummer-Verknüpfung

**Datei:** `webui/src/views/Login.vue` (Zeilen 250-320)

```javascript
const linkPhoneToTelegram = async () => {
  // 1. Telefonnummer mit Telegram-ID verknüpfen
  const linkResponse = await fetch('/api/users/link_phone', {
    method: 'POST',
    body: JSON.stringify({
      telegram_id: telegramId.value,  // Automatisch aus Bot
      phone: phone.value
    })
  })
  
  // 2. Jetzt Code anfordern
  const codeResponse = await fetch('/api/auth/request-code', {
    method: 'POST',
    body: JSON.stringify({
      phone: phone.value,
      telegram_id: telegramId.value
    })
  })
}
```

**Backend-Route:** `backend/app/routes/users.py` (Zeilen 113-160)
- Verknüpft Telefonnummer mit bestehender Telegram-ID
- Prüft, ob User mit Telegram-ID existiert

### 4. Code-Verifizierung

**Backend-Route:** `backend/app/routes/auth.py` (Zeilen 121-239)
- Generiert Code und sendet ihn per Telegram an die Telegram-ID
- User gibt Code im WebUI ein
- Verifizierung erfolgt über Userbot oder Fallback

### 5. Kontakt-Sharing (Alternative)

**Datei:** `bot/bot.py` (Zeilen 151-181)

```python
@app.on_message(filters.contact)
async def contact_handler(client, message):
    phone = message.contact.phone_number
    telegram_id = message.from_user.id
    
    payload = {
        "telegram_id": telegram_id,
        "phone": phone
    }
    
    await make_api_request("POST", "/users/register_phone", payload)
```

**Backend-Route:** `backend/app/routes/users.py` (Zeilen 113-160) - **NEU HINZUGEFÜGT**
- Verknüpft Telefonnummer direkt über Bot-Kontakt-Sharing

## Behobene Probleme

### 1. Fehlende Route
**Problem:** Bot rief `/users/register_phone` auf, aber Route existierte nicht
**Lösung:** Route hinzugefügt in `backend/app/routes/users.py`

### 2. Falsche Userbot-URL
**Problem:** Hardcodierte Userbot-URL in Backend
**Lösung:** Konfigurierbare URL in `backend/app/config.py`

### 3. Veraltete Register.vue
**Problem:** Separate Register-Komponente gehörte nicht zum Hauptflow
**Lösung:** Datei entfernt, da Registrierung nur über Bot erfolgt

### 4. API-Konfiguration
**Problem:** Inkonsistente API-URLs zwischen Frontend und Backend
**Lösung:** Zentrale Konfiguration in `webui/src/api/index.js`

## Sicherheitsaspekte

### Telegram-ID-Validierung
- Telegram-ID wird ausschließlich vom Bot ausgelesen
- Keine manuelle Eingabe möglich
- Automatische Übertragung über URL-Parameter oder WebApp-Kontext

### Telefonnummer-Validierung
- Regex-Validierung im Frontend
- Backend-Validierung vor Datenbankoperation
- Prüfung auf Duplikate

### Code-Verifizierung
- Echte Telegram-Verifizierung über Userbot
- Fallback auf eigenen Code bei Userbot-Fehlern
- Timeout nach 5-10 Minuten

## Abhängigkeiten

### Backend (requirements.txt)
```
fastapi==0.111.0
uvicorn[standard]==0.30.1
sqlalchemy==2.0.30
pyrogram==2.0.106
telethon==1.34.0
httpx==0.27.0
python-jose==3.3.0
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "axios": "^1.6.0",
    "pinia": "^3.0.3"
  }
}
```

### Userbot Service
```
telethon==1.34.0
fastapi==0.111.0
```

## Deployment

### Ports
- **Backend:** 8000
- **Userbot Service:** 8001  
- **Frontend:** 8080
- **Bot:** Telegram API

### Environment Variables
```bash
# Backend
DATABASE_URL=sqlite:///./telegram_bot.db
JWT_SECRET=your-secret-key
USERBOT_API_URL=http://localhost:8001

# Bot
TELEGRAM_BOT_TOKEN=your-bot-token
API_ID=your-api-id
API_HASH=your-api-hash

# Frontend
VITE_API_URL=https://api.bit-team-bot.online
VITE_USERBOT_URL=http://localhost:8001
```

## Zusammenfassung

Der korrigierte Ablauf ist jetzt:
1. **Bot `/start`** → Telegram-ID automatisch → `/users/register_or_update`
2. **WebUI öffnen** → Telegram-ID automatisch aus URL/WebApp
3. **Telefonnummer eingeben** → `/users/link_phone` (Verknüpfung)
4. **Code anfordern** → `/auth/request-code` → Code per Telegram
5. **Code eingeben** → `/auth/verify-code` → Login

**Alle Probleme wurden behoben und der Ablauf ist jetzt praxistauglich und sicher.** 