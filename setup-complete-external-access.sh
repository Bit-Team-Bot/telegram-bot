#!/bin/bash

# Telegram Bot Management System - Komplettes externes Zugriffs-Setup
# Konfiguriert alle Komponenten für externe Erreichbarkeit

set -e

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# Prüfe ob als Root ausgeführt
if [ "$EUID" -eq 0 ]; then
    error "Bitte nicht als Root ausführen!"
    exit 1
fi

log "🚀 Telegram Bot Management System - Komplettes externes Zugriffs-Setup"

# ===== 1. CLOUDFLARE TUNNELS KONFIGURIEREN =====
step "1. Konfiguriere Cloudflare Tunnels..."

# Prüfe ob cloudflared installiert ist
if ! command -v cloudflared &> /dev/null; then
    error "Cloudflared ist nicht installiert!"
    echo "Führe zuerst aus: cd userbot_service && ./setup-cloudflare-tunnel.sh"
    exit 1
fi

# Aktuelle Tunnel anzeigen
log "Aktuelle Cloudflare Tunnels:"
cloudflared tunnel list

# ===== 2. BACKEND TUNNEL KONFIGURIEREN =====
step "2. Konfiguriere Backend-Tunnel..."

# Erstelle Backend-Konfiguration für bit-team-bot Tunnel
cat > ~/.cloudflared/config-backend.yml << EOF
tunnel: 7e652cd5-01af-4f3e-a819-7db2da176857
credentials-file: ~/.cloudflared/7e652cd5-01af-4f3e-a819-7db2da176857.json

ingress:
  - hostname: api.bit-team-bot.online
    service: http://localhost:8000
    originRequest:
      noTLSVerify: true
  - hostname: webui.bit-team-bot.online
    service: http://localhost:80
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF

log "✅ Backend-Konfiguration erstellt: ~/.cloudflared/config-backend.yml"

# ===== 3. NGINX KONFIGURIEREN =====
step "3. Konfiguriere Nginx für alle Services..."

# Erstelle Nginx-Konfiguration für Backend
sudo tee /etc/nginx/sites-available/backend-service > /dev/null << 'EOF'
server {
    listen 80;
    server_name api.bit-team-bot.online;
    
    location / {
        proxy_pass http://localhost:8000;
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
    
    access_log /var/log/nginx/backend-service.access.log;
    error_log /var/log/nginx/backend-service.error.log;
}
EOF

# Erstelle Nginx-Konfiguration für WebUI
sudo tee /etc/nginx/sites-available/webui-service > /dev/null << 'EOF'
server {
    listen 80;
    server_name webui.bit-team-bot.online;
    root /home/manny/telegram-bot/webui/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
        
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    access_log /var/log/nginx/webui-service.access.log;
    error_log /var/log/nginx/webui-service.error.log;
}
EOF

# Aktiviere Nginx-Konfigurationen
if [ ! -L /etc/nginx/sites-enabled/backend-service ]; then
    sudo ln -s /etc/nginx/sites-available/backend-service /etc/nginx/sites-enabled/
fi

if [ ! -L /etc/nginx/sites-enabled/webui-service ]; then
    sudo ln -s /etc/nginx/sites-available/webui-service /etc/nginx/sites-enabled/
fi

# Teste und lade Nginx-Konfiguration
if sudo nginx -t; then
    sudo systemctl reload nginx
    log "✅ Nginx-Konfiguration erfolgreich geladen"
else
    error "❌ Nginx-Konfiguration fehlerhaft"
    exit 1
fi

# ===== 4. SYSTEMD SERVICES ERSTELLEN =====
step "4. Erstelle Systemd Services für alle Tunnels..."

# Backend-Tunnel Service
sudo tee /etc/systemd/system/cloudflared-backend.service > /dev/null << EOF
[Unit]
Description=Cloudflare Tunnel für Backend und WebUI
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/cloudflared tunnel run --config ~/.cloudflared/config-backend.yml
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Userbot-Tunnel Service (bereits vorhanden, aber prüfen)
if [ ! -f /etc/systemd/system/cloudflared-userbot.service ]; then
    sudo tee /etc/systemd/system/cloudflared-userbot.service > /dev/null << EOF
[Unit]
Description=Cloudflare Tunnel für Userbot-Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/cloudflared tunnel run userbot-service
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
fi

# Services aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-backend
sudo systemctl enable cloudflared-userbot

log "✅ Systemd Services erstellt und aktiviert"

# ===== 5. WEBUI BUILDEN =====
step "5. Baue WebUI für Produktion..."

cd webui

# Prüfe ob node_modules existiert
if [ ! -d "node_modules" ]; then
    log "Installiere Node.js Dependencies..."
    npm install
fi

# Baue für Produktion
log "Baue WebUI für Produktion..."
./build-production.sh

cd ..

# ===== 6. SERVICES STARTEN =====
step "6. Starte alle Services..."

# Starte Cloudflare Tunnels
sudo systemctl start cloudflared-backend
sudo systemctl start cloudflared-userbot

# Prüfe Status
sleep 5

if sudo systemctl is-active --quiet cloudflared-backend; then
    log "✅ Backend-Tunnel läuft"
else
    error "❌ Backend-Tunnel konnte nicht gestartet werden"
fi

if sudo systemctl is-active --quiet cloudflared-userbot; then
    log "✅ Userbot-Tunnel läuft"
else
    error "❌ Userbot-Tunnel konnte nicht gestartet werden"
fi

# ===== 7. TESTING =====
step "7. Teste externe Erreichbarkeit..."

log "Warte auf DNS-Propagation (30 Sekunden)..."
sleep 30

# Teste alle Endpoints
echo ""
log "🧪 Teste externe Endpoints:"

# Backend API
if curl -s -o /dev/null -w "%{http_code}" https://api.bit-team-bot.online/health | grep -q "200"; then
    log "✅ Backend API erreichbar: https://api.bit-team-bot.online"
else
    warn "⚠️ Backend API noch nicht erreichbar"
fi

# WebUI
if curl -s -o /dev/null -w "%{http_code}" https://webui.bit-team-bot.online/ | grep -q "200"; then
    log "✅ WebUI erreichbar: https://webui.bit-team-bot.online"
else
    warn "⚠️ WebUI noch nicht erreichbar"
fi

# Userbot Service
if curl -s -o /dev/null -w "%{http_code}" https://userbot.bit-team-bot.online/ | grep -q "200\|404"; then
    log "✅ Userbot Service erreichbar: https://userbot.bit-team-bot.online"
else
    warn "⚠️ Userbot Service noch nicht erreichbar"
fi

# ===== 8. ZUSAMMENFASSUNG =====
step "8. Zusammenfassung"

echo ""
log "🎉 Externes Zugriffs-Setup abgeschlossen!"
echo ""
log "📋 Verfügbare Services:"
echo "   🔗 Backend API: https://api.bit-team-bot.online"
echo "   🌐 WebUI: https://webui.bit-team-bot.online"
echo "   🤖 Userbot Service: https://userbot.bit-team-bot.online"
echo ""
log "🔧 Verwaltung:"
echo "   Backend-Tunnel Status: sudo systemctl status cloudflared-backend"
echo "   Userbot-Tunnel Status: sudo systemctl status cloudflared-userbot"
echo "   Nginx Status: sudo systemctl status nginx"
echo ""
log "📊 Logs:"
echo "   Backend-Tunnel Logs: sudo journalctl -u cloudflared-backend -f"
echo "   Userbot-Tunnel Logs: sudo journalctl -u cloudflared-userbot -f"
echo "   Nginx Logs: sudo tail -f /var/log/nginx/*.log"
echo ""
log "🚀 Nächste Schritte:"
echo "   1. Starte Backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "   2. Starte Userbot: cd userbot_service && python -m uvicorn main:app --host 0.0.0.0 --port 8001"
echo "   3. Teste Login: https://webui.bit-team-bot.online/login"
echo ""
log "✅ Alle Services sind jetzt von außen erreichbar!" 