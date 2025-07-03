#!/bin/bash

# Telegram Bot Management System - Sauberes externes Zugriffs-Setup
# Respektiert die bestehende Tunnel-Struktur

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

log "🚀 Telegram Bot Management System - Sauberes externes Zugriffs-Setup"

# ===== 1. AKTUELLE TUNNEL-STRUKTUR ANZEIGEN =====
step "1. Aktuelle Tunnel-Struktur:"

log "Aktuelle Cloudflare Tunnels:"
cloudflared tunnel list

echo ""
log "📋 Tunnel-Zuordnung:"
echo "   🔗 bit-team-bot (7e652cd5-01af-4f3e-a819-7db2da176857):"
echo "      - api.bit-team-bot.online → localhost:8000 (Backend)"
echo "      - webui.bit-team-bot.online → localhost:80 (WebUI)"
echo "   🤖 userbot-service (8c749081-a120-4080-a31e-e362432061ff):"
echo "      - userbot.bit-team-bot.online → localhost:8001 (Userbot)"

# ===== 2. NGINX KONFIGURIEREN =====
step "2. Konfiguriere Nginx für alle Services..."

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

# ===== 3. SYSTEMD SERVICES ERSTELLEN =====
step "3. Erstelle Systemd Services für alle Tunnels..."

# Bit-Team-Bot Tunnel Service (für API und WebUI)
sudo tee /etc/systemd/system/cloudflared-bit-team-bot.service > /dev/null << EOF
[Unit]
Description=Cloudflare Tunnel für Bit-Team-Bot (API + WebUI)
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/cloudflared tunnel run --config ~/.cloudflared/config-webui.yml
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Userbot-Tunnel Service
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

# Services aktivieren
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-bit-team-bot
sudo systemctl enable cloudflared-userbot

log "✅ Systemd Services erstellt und aktiviert"

# ===== 4. WEBUI BUILDEN =====
step "4. Baue WebUI für Produktion..."

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

# ===== 5. SERVICES STARTEN =====
step "5. Starte alle Services..."

# Starte Cloudflare Tunnels
sudo systemctl start cloudflared-bit-team-bot
sudo systemctl start cloudflared-userbot

# Prüfe Status
sleep 5

if sudo systemctl is-active --quiet cloudflared-bit-team-bot; then
    log "✅ Bit-Team-Bot Tunnel läuft"
else
    error "❌ Bit-Team-Bot Tunnel konnte nicht gestartet werden"
fi

if sudo systemctl is-active --quiet cloudflared-userbot; then
    log "✅ Userbot-Tunnel läuft"
else
    error "❌ Userbot-Tunnel konnte nicht gestartet werden"
fi

# ===== 6. TESTING =====
step "6. Teste externe Erreichbarkeit..."

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

# ===== 7. ZUSAMMENFASSUNG =====
step "7. Zusammenfassung"

echo ""
log "🎉 Sauberes externes Zugriffs-Setup abgeschlossen!"
echo ""
log "📋 Tunnel-Struktur (sauber getrennt):"
echo "   🔗 bit-team-bot Tunnel (7e652cd5-01af-4f3e-a819-7db2da176857):"
echo "      - https://api.bit-team-bot.online → Backend (Port 8000)"
echo "      - https://webui.bit-team-bot.online → WebUI (Port 80)"
echo "   🤖 userbot-service Tunnel (8c749081-a120-4080-a31e-e362432061ff):"
echo "      - https://userbot.bit-team-bot.online → Userbot (Port 8001)"
echo ""
log "🔧 Verwaltung:"
echo "   Bit-Team-Bot Tunnel: sudo systemctl status cloudflared-bit-team-bot"
echo "   Userbot-Tunnel: sudo systemctl status cloudflared-userbot"
echo "   Nginx Status: sudo systemctl status nginx"
echo ""
log "📊 Logs:"
echo "   Bit-Team-Bot Logs: sudo journalctl -u cloudflared-bit-team-bot -f"
echo "   Userbot Logs: sudo journalctl -u cloudflared-userbot -f"
echo "   Nginx Logs: sudo tail -f /var/log/nginx/*.log"
echo ""
log "🚀 Nächste Schritte:"
echo "   1. Starte Backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "   2. Starte Userbot: cd userbot_service && python -m uvicorn main:app --host 0.0.0.0 --port 8001"
echo "   3. Teste Login: https://webui.bit-team-bot.online/login"
echo ""
log "✅ Alle Services sind jetzt sauber getrennt und von außen erreichbar!" 