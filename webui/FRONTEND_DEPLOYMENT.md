# 🌐 Frontend Deployment & Network Error Lösung

## Problem: Network Error beim Login

Das **Network Error** Problem entsteht, weil das Frontend als statische Dateien im `dist`-Ordner läuft, aber die API-URLs nicht korrekt konfiguriert sind.

## 🔍 Diagnose

### 1. Aktuelle Situation prüfen
```bash
cd webui
node debug-production.js
```

### 2. Prüfe welche APIs erreichbar sind
- ✅ Backend: `https://api.bit-team-bot.online`
- ✅ Userbot: `https://userbot.bit-team-bot.online` (optional)
- ✅ Frontend: `https://webui.bit-team-bot.online`

## 🚀 Lösungen

### Option 1: Produktions-Build (empfohlen für öffentlichen Zugriff)

```bash
cd webui
./build-production.sh
```

**Was passiert:**
- Frontend wird mit öffentlichen API-URLs gebaut
- `dist/` Ordner enthält die produzierten Dateien
- APIs gehen an `https://api.bit-team-bot.online`

**Verwendung:**
```bash
# Statischen Server starten
cd dist
python3 -m http.server 8080

# Oder nginx verwenden
sudo cp -r dist/* /var/www/html/
```

### Option 2: Lokaler Build (für Entwicklung)

```bash
cd webui
./build-local.sh
```

**Was passiert:**
- Frontend wird mit lokalen API-URLs gebaut
- APIs gehen an `http://localhost:8000`
- Für lokale Entwicklung geeignet

**Verwendung:**
```bash
# Backend lokal starten
cd backend
source ../venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend lokal starten
cd webui/dist
python3 -m http.server 8080
```

## 🔧 Deployment-Optionen

### 1. Nginx (empfohlen)
```nginx
server {
    listen 80;
    server_name webui.bit-team-bot.online;
    
    location / {
        root /var/www/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API-Proxy (optional)
    location /api/ {
        proxy_pass https://api.bit-team-bot.online/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Apache
```apache
<VirtualHost *:80>
    ServerName webui.bit-team-bot.online
    DocumentRoot /var/www/html
    
    <Directory /var/www/html>
        AllowOverride All
        Require all granted
    </Directory>
    
    # Rewrite für Vue Router
    RewriteEngine On
    RewriteBase /
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /index.html [L]
</VirtualHost>
```

### 3. Python HTTP Server (für Tests)
```bash
cd webui/dist
python3 -m http.server 8080
```

## 🧪 Testing

### 1. Produktions-APIs testen
```bash
cd webui
node debug-production.js
```

### 2. Lokale APIs testen
```bash
cd webui
node debug-connection.js
```

### 3. Frontend testen
```bash
# Öffne im Browser:
# Produktion: https://webui.bit-team-bot.online/login
# Lokal: http://localhost:8080/login
```

## 🔄 Workflow

### Für Entwicklung:
1. **Backend starten**: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
2. **Frontend bauen**: `cd webui && ./build-local.sh`
3. **Frontend starten**: `cd webui/dist && python3 -m http.server 8080`
4. **Testen**: `http://localhost:8080/login`

### Für Produktion:
1. **Frontend bauen**: `cd webui && ./build-production.sh`
2. **Deployen**: `dist/` Ordner auf Webserver kopieren
3. **Testen**: `https://webui.bit-team-bot.online/login`

## 🚨 Häufige Probleme

### 1. CORS-Fehler
**Symptom**: `Access to fetch at 'https://api.bit-team-bot.online' from origin 'http://localhost:8080' has been blocked by CORS policy`

**Lösung**: Backend muss CORS für die Frontend-Domain erlauben

### 2. SSL-Zertifikat-Fehler
**Symptom**: `ERR_CERT_AUTHORITY_INVALID`

**Lösung**: Gültiges SSL-Zertifikat für die Domain installieren

### 3. DNS-Auflösung
**Symptom**: `ENOTFOUND`

**Lösung**: DNS-Einträge für die Domains prüfen

## ✅ Erfolgreiche Konfiguration

Nach korrekter Konfiguration sollte das Login funktionieren:

1. **Telefonnummer eingeben** → Code wird per Telegram-Bot gesendet
2. **Code eingeben** → Login erfolgreich
3. **Weiterleitung zum Dashboard**

## 🎯 Empfehlung

**Für öffentlichen Zugriff:**
- Verwende `./build-production.sh`
- Deploye auf Webserver mit SSL
- Teste mit `node debug-production.js`

**Für lokale Entwicklung:**
- Verwende `./build-local.sh`
- Starte Backend lokal
- Teste mit `node debug-connection.js` 