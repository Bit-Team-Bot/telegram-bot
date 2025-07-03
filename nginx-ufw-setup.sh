#!/bin/bash

# Nginx & UFW Setup für Telegram-Bot
set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Prüfe ob als Root ausgeführt
if [ "$EUID" -eq 0 ]; then
    error "Bitte nicht als Root ausführen!"
    exit 1
fi

log "🔧 Nginx & UFW Setup für Telegram-Bot..."

# 1. Nginx-Config erstellen
step "1. Erstelle Nginx-Konfiguration..."

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

log "✅ Nginx-Konfiguration erstellt"

# 2. Nginx-Config aktivieren
step "2. Aktiviere Nginx-Konfiguration..."

if [ ! -L /etc/nginx/sites-enabled/userbot-service ]; then
    sudo ln -s /etc/nginx/sites-available/userbot-service /etc/nginx/sites-enabled/
    log "✅ Symlink erstellt"
else
    log "✅ Symlink existiert bereits"
fi

# 3. Nginx-Konfiguration testen
step "3. Teste Nginx-Konfiguration..."

if sudo nginx -t; then
    sudo systemctl reload nginx
    log "✅ Nginx-Konfiguration erfolgreich geladen"
else
    error "❌ Nginx-Konfiguration fehlerhaft"
    exit 1
fi

# 4. UFW-Regeln konfigurieren
step "4. Konfiguriere UFW-Regeln..."

# Basis-Regeln
log "Füge Basis-Regeln hinzu..."
sudo ufw allow ssh 2>/dev/null || true
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true
sudo ufw allow 8000/tcp 2>/dev/null || true
sudo ufw allow from 127.0.0.1 to any port 8001 2>/dev/null || true
sudo ufw allow from 127.0.0.1 to any port 3000 2>/dev/null || true

# Cloudflare IPs
log "Füge Cloudflare IPs hinzu..."
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

log "✅ UFW-Regeln konfiguriert"

# 5. UFW aktivieren
step "5. Aktiviere UFW..."

if ! sudo ufw status | grep -q "Status: active"; then
    echo "y" | sudo ufw enable
    log "✅ UFW aktiviert"
else
    log "✅ UFW bereits aktiv"
fi

# 6. Status anzeigen
step "6. Zeige Status..."

echo ""
log "📋 Nginx-Status:"
sudo systemctl status nginx --no-pager -l

echo ""
log "📋 UFW-Status:"
sudo ufw status numbered

echo ""
log "🎉 Setup abgeschlossen!"
echo ""
log "🔧 Verwaltung:"
echo "   Nginx-Status: sudo systemctl status nginx"
echo "   Nginx-Logs: sudo tail -f /var/log/nginx/userbot-service.access.log"
echo "   UFW-Status: sudo ufw status numbered"
echo "   UFW-Logs: sudo tail -f /var/log/ufw.log"
echo ""
log "🧪 Testing:"
echo "   curl -I http://userbot.bit-team-bot.online/"
echo "   curl -X OPTIONS http://userbot.bit-team-bot.online/start -H 'Origin: https://webui.bit-team-bot.online'"
echo ""
log "🌐 Nächste Schritte:"
echo "   1. SSL-Zertifikat: sudo certbot --nginx -d userbot.bit-team-bot.online"
echo "   2. Userbot starten: cd userbot_service && python -m uvicorn main:app --host 0.0.0.0 --port 8001"
echo "   3. Frontend bauen: cd webui && ./build-production.sh"

echo ""
log "✅ Dein Server ist jetzt sicher konfiguriert!" 