# Bit-Team Bot API Dokumentation

## Übersicht

Die Bit-Team Bot API ist eine RESTful API, die auf FastAPI basiert und JWT-Token für die Authentifizierung verwendet.

**Base URL:** `https://api.bit-team-bot.online`  
**API Version:** 1.0.0  
**Content-Type:** `application/json`

## Authentifizierung

Die API verwendet JWT-Token für die Authentifizierung. Token müssen im `Authorization`-Header mit dem Format `Bearer <token>` gesendet werden.

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Endpoints

### 🔐 Authentifizierung

#### POST /auth/request_code
Fordert einen Verifizierungscode für die Telefonnummer an.

**Request Body:**
```json
{
  "phone": "+491701234567",
  "telegram_id": "123456789"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Code wurde gesendet"
}
```

**Fehler (400):**
```json
{
  "detail": "Ungültiges Telefonnummer-Format"
}
```

#### POST /auth/login
Verifiziert den Code und erstellt einen JWT-Token.

**Request Body:**
```json
{
  "phone": "+491701234567",
  "code": "123456",
  "telegram_id": "123456789"
}
```

**Response (200):**
```json
{
  "status": "success",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": 1,
  "telegram_id": "123456789",
  "is_superadmin": false,
  "phone": "+491701234567"
}
```

**Fehler (401):**
```json
{
  "detail": "Ungültiger Code"
}
```

#### GET /auth/validate
Validiert den aktuellen JWT-Token.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "status": "valid",
  "user_id": 1,
  "telegram_id": "123456789",
  "is_superadmin": false
}
```

### 📦 Pakete

#### GET /packages
Ruft alle verfügbaren Pakete ab.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "name": "Basic",
    "price_usdt": 99,
    "duration_days": 30,
    "signals_allowed": 10,
    "features": ["Basic Signals", "1 Trading Group", "E-Mail Support"]
  },
  {
    "id": 2,
    "name": "Pro",
    "price_usdt": 299,
    "duration_days": 90,
    "signals_allowed": 50,
    "features": ["Premium Signals", "3 Trading Groups", "Telegram Support"]
  }
]
```

#### POST /packages/purchase
Kauft ein Paket.

**Headers:**
```http
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "package_id": 2,
  "payment_method": "usdt"
}
```

**Response (200):**
```json
{
  "status": "success",
  "payment_url": "https://payment-gateway.com/pay/...",
  "order_id": "order_123456"
}
```

### 💰 Zahlungen

#### GET /payments
Ruft Zahlungshistorie ab.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "amount_usdt": 299,
    "status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "package_name": "Pro"
  }
]
```

#### GET /payments/current
Ruft aktuelles Abonnement ab.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "package_name": "Pro",
  "expires_at": "2024-04-15T10:30:00Z",
  "days_remaining": 45,
  "signals_used": 23,
  "signals_remaining": 27
}
```

### 👥 Benutzer

#### GET /users/profile
Ruft Benutzerprofil ab.

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "id": 1,
  "telegram_id": "123456789",
  "phone": "+491701234567",
  "is_superadmin": false,
  "created_at": "2024-01-01T00:00:00Z",
  "current_package": {
    "name": "Pro",
    "expires_at": "2024-04-15T10:30:00Z"
  }
}
```

#### PUT /users/profile
Aktualisiert Benutzerprofil.

**Headers:**
```http
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "phone": "+491701234568"
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Profil aktualisiert"
}
```

### 🔧 Admin (Nur Superadmin)

#### GET /admin/users
Ruft alle Benutzer ab (nur Superadmin).

**Headers:**
```http
Authorization: Bearer <token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "telegram_id": "123456789",
    "phone": "+491701234567",
    "is_superadmin": false,
    "created_at": "2024-01-01T00:00:00Z",
    "current_package": "Pro"
  }
]
```

#### PUT /admin/users/{user_id}
Aktualisiert Benutzer (nur Superadmin).

**Headers:**
```http
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "is_superadmin": true
}
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Benutzer aktualisiert"
}
```

### 📊 Monitoring

#### GET /monitoring/performance
Ruft Performance-Metriken ab.

**Response (200):**
```json
{
  "total_requests": 1250,
  "avg_response_time": 0.045,
  "success_rate": 98.5,
  "top_endpoints": [
    ["GET /health", 450],
    ["POST /auth/login", 320]
  ],
  "error_distribution": {
    "404": 5,
    "500": 2
  }
}
```

#### GET /monitoring/system
Ruft System-Metriken ab.

**Response (200):**
```json
{
  "current_cpu": 15.2,
  "current_memory": 45.8,
  "current_disk": 23.1,
  "avg_cpu": 12.5,
  "avg_memory": 42.3,
  "avg_disk": 22.8,
  "active_connections": 25
}
```

#### GET /monitoring/errors
Ruft die neuesten Fehler ab.

**Response (200):**
```json
{
  "errors": [
    {
      "error_type": "ValidationError",
      "error_message": "Invalid phone number format",
      "endpoint": "/auth/request_code",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "total_errors": 1
}
```

### 🏥 Health Check

#### GET /health
Ruft System-Status ab.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Datenbank ist erreichbar"
    },
    "userbot_service": {
      "status": "healthy",
      "message": "Userbot-Service ist erreichbar"
    },
    "system_resources": {
      "status": "healthy",
      "message": "System-Ressourcen OK"
    }
  }
}
```

## Fehlercodes

| Code | Bedeutung | Beschreibung |
|------|-----------|--------------|
| 200 | OK | Request erfolgreich |
| 201 | Created | Ressource erstellt |
| 400 | Bad Request | Ungültige Request-Daten |
| 401 | Unauthorized | Authentifizierung erforderlich |
| 403 | Forbidden | Keine Berechtigung |
| 404 | Not Found | Ressource nicht gefunden |
| 429 | Too Many Requests | Rate-Limit überschritten |
| 500 | Internal Server Error | Server-Fehler |

## Rate Limiting

Die API implementiert Rate-Limiting:
- **Standard-Endpoints:** 100 Requests pro Stunde
- **Auth-Endpoints:** 5 Login-Versuche pro 15 Minuten
- **Admin-Endpoints:** 50 Requests pro Stunde

## Beispiele

### JavaScript (Fetch)
```javascript
// Login
const loginResponse = await fetch('https://api.bit-team-bot.online/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    phone: '+491701234567',
    code: '123456',
    telegram_id: '123456789'
  })
});

const loginData = await loginResponse.json();
const token = loginData.token;

// Pakete abrufen
const packagesResponse = await fetch('https://api.bit-team-bot.online/packages', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const packages = await packagesResponse.json();
```

### Python (requests)
```python
import requests

# Login
login_data = {
    'phone': '+491701234567',
    'code': '123456',
    'telegram_id': '123456789'
}

response = requests.post('https://api.bit-team-bot.online/auth/login', json=login_data)
token = response.json()['token']

# Pakete abrufen
headers = {'Authorization': f'Bearer {token}'}
packages = requests.get('https://api.bit-team-bot.online/packages', headers=headers)
```

### cURL
```bash
# Login
curl -X POST https://api.bit-team-bot.online/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+491701234567", "code": "123456", "telegram_id": "123456789"}'

# Pakete abrufen
curl -H "Authorization: Bearer <token>" \
  https://api.bit-team-bot.online/packages
```

## WebSocket-Endpoints

### /ws/notifications
WebSocket-Endpoint für Echtzeit-Benachrichtigungen.

**Verbindung:**
```javascript
const ws = new WebSocket('wss://api.bit-team-bot.online/ws/notifications');

ws.onmessage = function(event) {
  const notification = JSON.parse(event.data);
  console.log('Neue Benachrichtigung:', notification);
};
```

**Nachrichten-Format:**
```json
{
  "type": "signal",
  "data": {
    "coin": "BTC",
    "action": "BUY",
    "price": 45000,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## SDKs und Libraries

### Offizielle SDKs
- **JavaScript/TypeScript:** `@bit-team/api-client`
- **Python:** `bit-team-api-client`
- **PHP:** `bit-team/api-client`

### Community Libraries
- **Go:** `github.com/bit-team/go-api`
- **Rust:** `bit-team-api-rs`
- **Java:** `com.bitteam.api-client`

## Support

- **API-Dokumentation:** https://api.bit-team-bot.online/docs
- **GitHub Issues:** https://github.com/bit-team/bot/issues
- **Discord:** https://discord.gg/bit-team
- **E-Mail:** api-support@bit-team-bot.online 