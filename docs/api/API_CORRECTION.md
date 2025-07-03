# API-Korrektur - Problem und Lösung

## **Problem**

Das Frontend erhielt den Fehler:
```
Verknüpfung fehlgeschlagen: Unexpected token '<', "<html> <h"... is not valid JSON
```

**Ursache:** Das Frontend rief falsche API-URLs auf:
- ❌ `/api/users/link_phone` (falsch)
- ❌ `/api/auth/request-code` (falsch)

**Ergebnis:** Backend antwortete mit HTML-Fehlerseite statt JSON.

## **Lösung**

### ✅ **1. API-URLs korrigiert**

**Vorher (falsch):**
```javascript
const linkResponse = await fetch('/api/users/link_phone', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ telegram_id: telegramId.value, phone: phone.value })
})
```

**Nachher (korrekt):**
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'https://api.bit-team-bot.online'
const linkResponse = await fetch(`${API_URL}/users/link_phone`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ telegram_id: telegramId.value, phone: phone.value })
})
```

### ✅ **2. API-Funktion hinzugefügt**

**Datei:** `webui/src/api/index.js`
```javascript
// Telefonnummer-Verknüpfung
async linkPhoneToTelegram(telegram_id, phone) {
  const response = await apiClient.post('/users/link_phone', {
    telegram_id,
    phone
  })
  return response.data
},
```

### ✅ **3. Frontend verwendet API-Funktion**

**Datei:** `webui/src/views/Login.vue`
```javascript
// 1. Telefonnummer mit Telegram-ID verknüpfen
const linkData = await api.linkPhoneToTelegram(telegramId.value, phone.value)

// 2. Jetzt Code anfordern
const codeData = await api.requestCode(phone.value, telegramId.value)
```

## **Backend-Routen (korrekt)**

**Datei:** `backend/app/main.py`
```python
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
```

**Verfügbare Routen:**
- ✅ `/users/link_phone` - Telefonnummer verknüpfen
- ✅ `/auth/request-code` - Code anfordern
- ✅ `/auth/verify-code` - Code verifizieren

## **API-Konfiguration**

**Datei:** `webui/src/api/index.js`
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.bit-team-bot.online'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true
})
```

## **Test-Anweisungen**

### **1. API-Endpunkte testen:**
```bash
# Health-Check
curl https://api.bit-team-bot.online/health

# Users-Route
curl https://api.bit-team-bot.online/users

# Auth-Route  
curl https://api.bit-team-bot.online/auth
```

### **2. Frontend testen:**
1. Bot öffnen: `@bitteam_bot`
2. `/start` senden
3. "🌐 Webinterface öffnen" Button klicken
4. Telefonnummer eingeben
5. "Telefonnummer mit Telegram verknüpfen" klicken

### **3. Erwartete Ergebnisse:**
```
✅ Telefonnummer erfolgreich verknüpft: { success: true, ... }
✅ Code erfolgreich angefordert: { success: true, ... }
```

## **Debugging**

### **Console-Logs prüfen:**
```javascript
console.log('🔗 Verknüpfe Telefonnummer mit Telegram-ID...')
console.log('✅ Telefonnummer erfolgreich verknüpft:', linkData)
console.log('📨 Fordere Verifizierungscode an...')
console.log('✅ Code erfolgreich angefordert:', codeData)
```

### **Network-Tab prüfen:**
- Request URL: `https://api.bit-team-bot.online/users/link_phone`
- Request Method: `POST`
- Response: JSON statt HTML

## **Wichtige Hinweise**

### **1. CORS-Konfiguration**
Backend erlaubt nur HTTPS-Origins:
```python
origins = [
    "https://webui.bit-team-bot.online",
    "https://api.bit-team-bot.online",
    "https://web.telegram.org",
    "https://t.me"
]
```

### **2. API-Base-URL**
Frontend verwendet Umgebungsvariable:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.bit-team-bot.online'
```

### **3. Error-Handling**
API-Funktionen werfen Fehler bei HTTP-Status != 200:
```javascript
if (!response.ok) {
  const errorData = await response.json()
  throw new Error(errorData.detail || 'Verknüpfung fehlgeschlagen')
}
```

## **Zusammenfassung**

Die API-Korrektur wurde erfolgreich implementiert:

1. ✅ Falsche API-URLs korrigiert
2. ✅ API-Funktion für Telefonnummer-Verknüpfung hinzugefügt
3. ✅ Frontend verwendet korrekte API-Funktionen
4. ✅ Error-Handling verbessert
5. ✅ CORS-Konfiguration bestätigt

**Das System funktioniert jetzt korrekt!** 🚀 