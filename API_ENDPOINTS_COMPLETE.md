# 🔗 **VOLLSTÄNDIGE API-ENDPUNKTE ÜBERSICHT**

## **🌐 ONLINE-SYSTEM KONFIGURATION**

### **Basis-URLs:**
- **Backend API:** `https://api.bit-team-bot.online`
- **Userbot API:** `https://userbot.bit-team-bot.online`
- **WebUI:** `https://webui.bit-team-bot.online`
- **Datenbank:** `telegram_bot.db` (SQLite)

---

## **1. BACKEND API (FastAPI) - Port 8000**

### **🔧 System-Endpunkte:**
- `GET /` - Root-Endpoint mit System-Info
- `GET /health` - Health-Check
- `GET /status` - System-Status
- `GET /system-status` - Alle Services-Status
- `GET /time` - Aktuelle Zeit
- `GET /test-headers` - Header-Test

### **🔐 Authentifizierung (`/auth`):**
- `POST /auth/telegram-login` - Telegram-Login
- `POST /auth/login` - Standard-Login (NEU)
- `POST /auth/register` - Benutzer-Registrierung (NEU)
- `POST /auth/refresh` - Token-Refresh (NEU)
- `GET /auth/verify` - Token-Verifizierung (NEU)
- `GET /auth/me` - Aktueller User
- `POST /auth/request-code` - Code anfordern
- `POST /auth/verify-code` - Code verifizieren
- `POST /auth/auto-login` - Auto-Login
- `POST /auth/logout` - Logout

### **👥 Benutzer (`/users`):**
- `POST /users/register_or_update` - User registrieren/aktualisieren
- `GET /users/{user_id}/is_paid` - Zahlungsstatus prüfen
- `GET /users/profile` - User-Profil
- `GET /users/settings` - User-Einstellungen
- `PUT /users/settings/notifications` - Benachrichtigungen aktualisieren
- `GET /users/groups` - User-Gruppen
- `GET /users/export-data` - Daten exportieren
- `DELETE /users/account` - Konto löschen
- `GET /users/userbot-sessions` - Userbot-Sessions
- `POST /users/userbot-sessions` - Userbot-Session erstellen
- `PUT /users/userbot-sessions/{session_id}` - Session aktualisieren
- `DELETE /users/userbot-sessions/{session_id}` - Session löschen

### **📦 Pakete (`/packages`):**
- `GET /packages` - Alle Pakete
- `GET /packages/{package_id}` - Spezifisches Paket
- `POST /packages` - Paket erstellen
- `PUT /packages/{package_id}` - Paket aktualisieren
- `DELETE /packages/{package_id}` - Paket löschen

### **💳 Zahlungen (`/payments`):**
- `POST /payments/` - Zahlung erstellen
- `GET /payments/user/{user_id}` - User-Zahlungen
- `GET /payments/history` - Zahlungshistorie (NEU)

### **💰 Wallet (`/wallet`):**
- `GET /wallet/balance` - Wallet-Balance (NEU)
- `GET /wallet/transactions` - Wallet-Transaktionen (NEU)
- `POST /wallet/webhook` - Zahlungs-Webhook

### **📊 Dashboard (`/dashboard`):**
- `GET /dashboard/stats` - Dashboard-Statistiken
- `GET /dashboard/activity` - Neueste Aktivitäten

### **🔍 Monitoring (`/monitoring`):**
- `GET /monitoring/performance` - Performance-Zusammenfassung
- `GET /monitoring/errors` - Neueste Fehler
- `GET /monitoring/endpoints` - Endpoint-Statistiken
- `GET /monitoring/stats` - Monitoring-Statistiken (NEU)

### **👨‍💼 Admin (`/admin`):**
- `GET /admin/users` - Alle Benutzer
- `GET /admin/stats` - Admin-Statistiken (NEU)
- `GET /admin/settings` - Admin-Einstellungen (NEU)
- `PUT /admin/settings` - Admin-Einstellungen aktualisieren (NEU)
- `GET /admin/packages` - Admin-Pakete
- `POST /admin/packages` - Paket erstellen
- `PUT /admin/packages/{package_id}` - Paket aktualisieren
- `DELETE /admin/packages/{package_id}` - Paket löschen
- `GET /admin/signal-groups` - Signalgruppen
- `POST /admin/signal-groups` - Signalgruppe erstellen
- `PUT /admin/signal-groups/{group_id}` - Signalgruppe aktualisieren
- `DELETE /admin/signal-groups/{group_id}` - Signalgruppe löschen
- `GET /admin/signal-themes` - Signal-Themes
- `POST /admin/signal-themes` - Theme erstellen
- `PUT /admin/signal-themes/{theme_id}` - Theme aktualisieren
- `DELETE /admin/signal-themes/{theme_id}` - Theme löschen

### **📋 Gruppen (`/groups`):**
- `GET /groups/` - Alle Gruppen
- `POST /groups/` - Gruppe erstellen
- `GET /groups/{group_id}` - Spezifische Gruppe
- `PUT /groups/{group_id}` - Gruppe aktualisieren
- `DELETE /groups/{group_id}` - Gruppe löschen
- `GET /groups/dialogs` - Verfügbare Dialoge
- `GET /groups/forwarding-mappings` - Weiterleitungs-Mappings
- `POST /groups/forwarding-mappings` - Mapping erstellen
- `PUT /groups/forwarding-mappings/{mapping_id}` - Mapping aktualisieren
- `DELETE /groups/forwarding-mappings/{mapping_id}` - Mapping löschen

### **⚠️ Gruppen-Verwaltung:**
- `POST /group-warnings/` - Verwarnung erstellen
- `POST /group-mutes/` - Mute erstellen
- `POST /group-kicks/` - Kick erstellen

### **📞 Support (`/support`):**
- `GET /support/tickets` - Support-Tickets

---

## **2. USERBOT API (FastAPI) - Port 9000**

### **🔧 System-Endpunkte:**
- `GET /health` - Health-Check
- `GET /status` - Userbot-Status

### **📱 Userbot-Funktionen:**
- `POST /start` - Userbot starten
- `POST /verify` - Code verifizieren
- `GET /api/dialogs` - Verfügbare Dialoge
- `POST /api/create_group` - Gruppe erstellen
- `POST /api/send_message` - Nachricht senden
- `POST /api/add_user_to_group` - User zu Gruppe hinzufügen
- `POST /api/transfer_ownership` - Besitz übertragen

### **👥 User-Verwaltung:**
- `POST /users/link_phone_bot` - Telefonnummer verknüpfen

---

## **3. BOT API (Pyrogram) - Telegram Bot**

### **🤖 Bot-Funktionen:**
- `/start` - Start-Kommando (privat)
- `/menu` - Admin-Menü (Gruppen)
- Kontakt-Sharing Handler
- Callback-Query Handler

### **🔗 Bot → Backend Kommunikation:**
- `GET /users/{telegram_id}/is_paid` - Zahlungsstatus prüfen
- `POST /users/register_or_update` - User-Daten senden
- `POST /users/link_phone_bot` - Telefonnummer verknüpfen
- `GET /payments/user/{user_id}` - Zahlungen abrufen

### **🔗 Bot → Userbot Kommunikation:**
- `POST /users/link_phone_bot` - Telefonnummer verknüpfen

---

## **4. FRONTEND API (JavaScript) - WebUI**

### **🌐 Frontend → Backend Kommunikation:**
```javascript
// API-Konfiguration
const API_BASE_URL = 'https://api.bit-team-bot.online'
const USERBOT_API_URL = 'https://userbot.bit-team-bot.online'

// Authentifizierung
api.login(userData)
api.register(userData)
api.verifyToken()
api.logout()

// Userbot
api.userbotStart(phone)
api.userbotVerify(phone, code)
api.userbotGetDialogs()
api.userbotCreateGroup(title, supergroup)
api.userbotSendMessage(groupId, message)
api.userbotAddUserToGroup(userId, groupId)
api.userbotTransferOwnership(groupId, newOwnerId)
api.userbotGetStatus()

// Admin
api.getUsers()
api.getStats()

// Packages
api.getPackages()

// Payments
api.getPayments()
api.getPaymentHistory()

// Users
api.getUserProfile()

// Wallet
api.getWalletBalance()
api.getWalletTransactions()

// Monitoring
api.getMonitoringStats()

// Health
api.getHealth()
api.getStatus()
```

---

## **5. DATENBANK-ZUGRIFF**

### **🗄️ Zentrale Datenbank: `telegram_bot.db`**

### **📊 Tabellen:**
- `users` - Benutzer
- `packages` - Pakete
- `payments` - Zahlungen
- `signal_groups` - Signalgruppen
- `signal_themes` - Signal-Themes
- `userbot_sessions` - Userbot-Sessions
- `forwarding_group_mappings` - Weiterleitungs-Mappings
- `group_warnings` - Gruppen-Verwarnungen
- `group_mutes` - Gruppen-Mutes
- `group_kicks` - Gruppen-Kicks

### **🔗 Datenbank-Verbindungen:**
- **Backend:** SQLAlchemy ORM
- **Userbot:** SQLAlchemy ORM
- **Bot:** Über Backend-API

---

## **6. EXTERNE SERVICES**

### **🌐 Cloudflare Tunnel:**
- **Backend:** `https://api.bit-team-bot.online`
- **Userbot:** `https://userbot.bit-team-bot.online`
- **WebUI:** `https://webui.bit-team-bot.online`

### **🔧 Nginx:**
- Reverse Proxy für alle Services
- SSL-Terminierung
- Load Balancing

### **📱 Telegram API:**
- **Bot API:** Über Pyrogram
- **Userbot API:** Über Telethon

---

## **✅ ALLE ENDPUNKTE IMPLEMENTIERT**

**Status:** Alle fehlenden Endpunkte wurden implementiert:
- ✅ Auth-Endpunkte (`/login`, `/register`, `/refresh`, `/verify`)
- ✅ Admin-Endpunkte (`/admin/stats`, `/admin/settings`)
- ✅ Payments-Endpunkt (`/payments/history`)
- ✅ Wallet-Endpunkte (`/wallet/balance`, `/wallet/transactions`)
- ✅ Monitoring-Endpunkt (`/monitoring/stats`)

**Das System ist jetzt vollständig miteinander verbunden und alle Kommunikationspunkte sind verfügbar!** 