#!/bin/bash

# Cloudflare Tunnel Setup für Userbot-Service
# Dieses Skript richtet automatisch einen Cloudflare Tunnel ein

set -e  # Beende bei Fehlern

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Prüfe ob als Root ausgeführt
if [ "$EUID" -eq 0 ]; then
    error "Bitte nicht als Root ausführen!"
    exit 1
fi

log "🚀 Cloudflare Tunnel für Userbot-Service einrichten..."

# Schritt 1: Cloudflared installieren
step "1. Installiere cloudflared..."

if ! command -v cloudflared &> /dev/null; then
    log "Cloudflared nicht gefunden, installiere..."
    
    # Architektur ermitteln
    ARCH=$(uname -m)
    case $ARCH in
        x86_64)
            PACKAGE="cloudflared-linux-amd64.deb"
            ;;
        armv7l|armv8l)
            PACKAGE="cloudflared-linux-arm"
            ;;
        aarch64)
            PACKAGE="cloudflared-linux-arm64"
            ;;
        *)
            error "Unbekannte Architektur: $ARCH"
            exit 1
            ;;
    esac
    
    log "Architektur: $ARCH, Paket: $PACKAGE"
    
    # Download und Installation
    wget "https://github.com/cloudflare/cloudflared/releases/latest/download/$PACKAGE" -O /tmp/cloudflared
    chmod +x /tmp/cloudflared
    sudo mv /tmp/cloudflared /usr/local/bin/
    
    log "✅ Cloudflared installiert"
else
    log "✅ Cloudflared bereits installiert"
fi

# Schritt 2: Authentifizierung
step "2. Authentifiziere bei Cloudflare..."

if [ ! -f ~/.cloudflared/cert.pem ]; then
    log "Starte Authentifizierung..."
    cloudflared tunnel login
    
    if [ ! -f ~/.cloudflared/cert.pem ]; then
        error "Authentifizierung fehlgeschlagen!"
        exit 1
    fi
    log "✅ Authentifizierung erfolgreich"
else
    log "✅ Bereits authentifiziert"
fi

# Schritt 3: Tunnel erstellen
step "3. Erstelle Tunnel..."

# Prüfe ob Tunnel bereits existiert
if cloudflared tunnel list | grep -q "userbot-service"; then
    log "Tunnel 'userbot-service' existiert bereits"
    TUNNEL_ID=$(cloudflared tunnel list | grep "userbot-service" | awk '{print $1}')
    log "Tunnel-ID: $TUNNEL_ID"
else
    log "Erstelle neuen Tunnel..."
    TUNNEL_OUTPUT=$(cloudflared tunnel create userbot-service)
    TUNNEL_ID=$(echo "$TUNNEL_OUTPUT" | grep -o '[a-f0-9-]\{36\}')
    
    if [ -z "$TUNNEL_ID" ]; then
        error "Fehler beim Erstellen des Tunnels"
        exit 1
    fi
    
    log "✅ Tunnel erstellt: $TUNNEL_ID"
fi

# Schritt 4: Konfiguration erstellen
step "4. Erstelle Konfiguration..."

mkdir -p ~/.cloudflared

cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: userbot.bit-team-bot.online
    service: http://localhost:8001
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF

log "✅ Konfiguration erstellt: ~/.cloudflared/config.yml"

# Schritt 5: DNS-Record konfigurieren
step "5. Konfiguriere DNS-Record..."

log "Konfiguriere DNS-Record automatisch..."
cloudflared tunnel route dns userbot-service userbot.bit-team-bot.online

log "✅ DNS-Record konfiguriert"

# Schritt 6: Systemd Service erstellen
step "6. Erstelle Systemd Service..."

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

# Service aktivieren
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-userbot

log "✅ Systemd Service erstellt und aktiviert"

# Schritt 7: Service starten
step "7. Starte Service..."

sudo systemctl start cloudflared-userbot
sleep 3

if sudo systemctl is-active --quiet cloudflared-userbot; then
    log "✅ Service erfolgreich gestartet"
else
    error "Service konnte nicht gestartet werden"
    sudo systemctl status cloudflared-userbot
    exit 1
fi

# Schritt 8: Testing
step "8. Teste Verbindung..."

log "Warte auf DNS-Propagation (30 Sekunden)..."
sleep 30

# Test HTTP-Verbindung
if curl -s -o /dev/null -w "%{http_code}" https://userbot.bit-team-bot.online/ | grep -q "200\|404"; then
    log "✅ HTTP-Verbindung funktioniert"
else
    warn "HTTP-Verbindung noch nicht verfügbar (DNS-Propagation kann bis zu 5 Minuten dauern)"
fi

# Test API-Endpoint
if curl -s -o /dev/null -w "%{http_code}" https://userbot.bit-team-bot.online/status | grep -q "200"; then
    log "✅ API-Endpoint funktioniert"
else
    warn "API-Endpoint noch nicht verfügbar"
fi

# Schritt 9: Zusammenfassung
step "9. Zusammenfassung"

log "🎉 Cloudflare Tunnel erfolgreich eingerichtet!"
echo ""
log "📋 Konfiguration:"
echo "   Tunnel-ID: $TUNNEL_ID"
echo "   Domain: https://userbot.bit-team-bot.online"
echo "   Service: http://localhost:8001"
echo ""
log "🔧 Verwaltung:"
echo "   Status prüfen: sudo systemctl status cloudflared-userbot"
echo "   Logs anzeigen: sudo journalctl -u cloudflared-userbot -f"
echo "   Service neustarten: sudo systemctl restart cloudflared-userbot"
echo ""
log "🧪 Testing:"
echo "   curl https://userbot.bit-team-bot.online/"
echo "   curl https://userbot.bit-team-bot.online/status"
echo ""
log "🌐 Nächste Schritte:"
echo "   1. Starte Userbot-Service: cd userbot_service && python -m uvicorn main:app --host 0.0.0.0 --port 8001"
echo "   2. Baue Frontend neu: cd webui && ./build-production.sh"
echo "   3. Teste Login: https://webui.bit-team-bot.online/login"

echo ""
log "✅ Setup abgeschlossen!" 