# 🔧 Nginx & UFW Konfiguration für Cloudflare Tunnel

## 🌐 Nginx Konfiguration

### 1. Nginx-Config für Userbot-Service erstellen

```bash
sudo nano /etc/nginx/sites-available/userbot-service
```

**Inhalt:**
```nginx
server {
    listen 80;
    server_name userbot.bit-team-bot.online;
    
    # Weiterleitung an Cloudflare Tunnel (Port 8001)
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS-Header für Webinterface
        add_header 'Access-Control-Allow-Origin' 'https://webui.bit-team-bot.online' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        # Preflight-Requests behandeln
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://webui.bit-team-bot.online' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
    
    # Health-Check Endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Logs
    access_log /var/log/nginx/userbot-service.access.log;
    error_log /var/log/nginx/userbot-service.error.log;
}
```

### 2. Nginx-Config aktivieren

```bash
# Symlink erstellen
sudo ln -s /etc/nginx/sites-available/userbot-service /etc/nginx/sites-enabled/

# Nginx-Konfiguration testen
sudo nginx -t

# Nginx neu laden
sudo systemctl reload nginx
```

### 3. SSL-Zertifikat mit Certbot (optional)

```bash
# Certbot installieren
sudo apt install certbot python3-certbot-nginx

# SSL-Zertifikat erstellen
sudo certbot --nginx -d userbot.bit-team-bot.online

# Auto-Renewal testen
sudo certbot renew --dry-run
```

## 🔥 UFW Firewall Konfiguration

### 1. UFW-Status prüfen

```bash
sudo ufw status verbose
```

### 2. UFW-Regeln für Telegram-Bot

```bash
# SSH (falls noch nicht aktiviert)
sudo ufw allow ssh

# HTTP (Port 80)
sudo ufw allow 80/tcp

# HTTPS (Port 443)
sudo ufw allow 443/tcp

# Backend API (Port 8000)
sudo ufw allow 8000/tcp

# Userbot-Service (Port 8001) - nur lokal
sudo ufw allow from 127.0.0.1 to any port 8001

# Webinterface (Port 3000) - nur lokal
sudo ufw allow from 127.0.0.1 to any port 3000

# Cloudflare IPs erlauben (für Tunnel)
sudo ufw allow from 173.245.48.0/20
sudo ufw allow from 103.21.244.0/22
sudo ufw allow from 103.22.200.0/22
sudo ufw allow from 103.31.4.0/22
sudo ufw allow from 141.101.64.0/18
sudo ufw allow from 108.162.192.0/18
sudo ufw allow from 190.93.240.0/20
sudo ufw allow from 188.114.96.0/20
sudo ufw allow from 197.234.240.0/22
sudo ufw allow from 198.41.128.0/17
sudo ufw allow from 162.158.0.0/15
sudo ufw allow from 104.16.0.0/13
sudo ufw allow from 104.24.0.0/14
sudo ufw allow from 172.64.0.0/13
sudo ufw allow from 131.0.72.0/22
```

### 3. UFW aktivieren

```bash
# UFW aktivieren (falls noch nicht aktiv)
sudo ufw enable

# Status anzeigen
sudo ufw status numbered
```

## 🔧 Automatisiertes Setup-Skript

```bash
#!/bin/bash

# Nginx & UFW Setup für Telegram-Bot
set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

log "🔧 Nginx & UFW Setup für Telegram-Bot..."

# 1. Nginx-Config erstellen
log "1. Erstelle Nginx-Konfiguration..."

sudo tee /etc/nginx/sites-available/userbot-service > /dev/null << 'EOF'
server {
    listen 80;
    server_name userbot.bit-team-bot.online;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        add_header 'Access-Control-Allow-Origin' 'https://webui.bit-team-bot.online' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://webui.bit-team-bot.online' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    access_log /var/log/nginx/userbot-service.access.log;
    error_log /var/log/nginx/userbot-service.error.log;
}
EOF

# 2. Nginx-Config aktivieren
log "2. Aktiviere Nginx-Konfiguration..."

if [ ! -L /etc/nginx/sites-enabled/userbot-service ]; then
    sudo ln -s /etc/nginx/sites-available/userbot-service /etc/nginx/sites-enabled/
fi

# 3. Nginx-Konfiguration testen
log "3. Teste Nginx-Konfiguration..."

if sudo nginx -t; then
    sudo systemctl reload nginx
    log "✅ Nginx-Konfiguration erfolgreich"
else
    error "❌ Nginx-Konfiguration fehlerhaft"
    exit 1
fi

# 4. UFW-Regeln konfigurieren
log "4. Konfiguriere UFW-Regeln..."

# Basis-Regeln
sudo ufw allow ssh 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
sudo ufw allow 8000/tcp 2>/dev/null || true
sudo ufw allow from 127.0.0.1 to any port 8001 2>/dev/null || true
sudo ufw allow from 127.0.0.1 to any port 3000 2>/dev/null || true

# Cloudflare IPs
CLOUDFLARE_IPS=(
    "173.245.48.0/20"
    "103.21.244.0/22"
    "103.22.200.0/22"
    "103.31.4.0/22"
    "141.101.64.0/18"
    "108.162.192.0/18"
    "190.93.240.0/20"
    "188.114.96.0/20"
    "197.234.240.0/22"
    "198.41.128.0/17"
    "162.158.0.0/15"
    "104.16.0.0/13"
    "104.24.0.0/14"
    "172.64.0.0/13"
    "131.0.72.0/22"
)

for ip in "${CLOUDFLARE_IPS[@]}"; do
    sudo ufw allow from "$ip" 2>/dev/null || true
done

# 5. UFW aktivieren
log "5. Aktiviere UFW..."

sudo ufw --force enable

log "✅ Setup abgeschlossen!"
log "📋 UFW-Status: sudo ufw status numbered"
log "📋 Nginx-Status: sudo systemctl status nginx"
```

## 🧪 Testing

### 1. Nginx-Test

```bash
# Nginx-Status
sudo systemctl status nginx

# Konfiguration testen
sudo nginx -t

# Logs anzeigen
sudo tail -f /var/log/nginx/userbot-service.access.log
```

### 2. UFW-Test

```bash
# UFW-Status
sudo ufw status numbered

# Regeln anzeigen
sudo ufw show added
```

### 3. Verbindung testen

```bash
# HTTP-Test
curl -I http://userbot.bit-team-bot.online/

# CORS-Test
curl -X OPTIONS http://userbot.bit-team-bot.online/start \
  -H "Origin: https://webui.bit-team-bot.online" \
  -H "Access-Control-Request-Method: POST"
```

## 🚨 Troubleshooting

### Nginx-Probleme

1. **Port bereits in Verwendung**
   ```bash
   sudo netstat -tlnp | grep :80
   sudo systemctl stop apache2  # falls Apache läuft
   ```

2. **Permission-Denied**
   ```bash
   sudo chown -R www-data:www-data /var/log/nginx/
   sudo chmod 755 /var/log/nginx/
   ```

### UFW-Probleme

1. **Regel nicht hinzugefügt**
   ```bash
   sudo ufw status numbered
   sudo ufw delete [NUMMER]
   ```

2. **Cloudflare IPs aktualisieren**
   ```bash
   # Aktuelle IPs von Cloudflare herunterladen
   curl -s https://www.cloudflare.com/ips-v4 | while read ip; do
       sudo ufw allow from "$ip"
   done
   ```

## ✅ Erfolgreiche Konfiguration

Nach korrekter Einrichtung:

1. **Nginx läuft**: `sudo systemctl status nginx`
2. **UFW aktiv**: `sudo ufw status`
3. **Userbot erreichbar**: `curl http://userbot.bit-team-bot.online/`
4. **CORS funktioniert**: OPTIONS-Requests werden korrekt beantwortet

## 🎯 Nächste Schritte

1. **Setup ausführen**: `./nginx-ufw-setup.sh`
2. **SSL-Zertifikat**: `sudo certbot --nginx -d userbot.bit-team-bot.online`
3. **Userbot starten**: `cd userbot_service && python -m uvicorn main:app --host 0.0.0.0 --port 8001`
4. **Frontend bauen**: `cd webui && ./build-production.sh`

**Dein Userbot-Service ist dann vollständig konfiguriert und sicher!** 🔒 