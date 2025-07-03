#!/bin/bash

# Telegram Bot Management System - Kompletter Debug Starter
# Startet Backend, Bot und WebUI-Debug mit vollständigem Logging

echo "🚀 Starte Telegram Bot Management System im Komplett-Debug-Modus..."

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log-Dateien
BACKEND_LOG="backend_debug.log"
BOT_LOG="bot_debug.log"
WEBUI_LOG="webui_debug.log"
BACKEND_PID_FILE=".backend_debug.pid"
BOT_PID_FILE=".bot_debug.pid"

# Funktion zum Beenden aller Services
cleanup() {
    echo -e "${YELLOW}🛑 Beende alle Services...${NC}"
    
    # Beende Backend
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        echo -e "${CYAN}📋 Beende Backend PID: $BACKEND_PID${NC}"
        kill -TERM $BACKEND_PID 2>/dev/null
        sleep 2
        kill -KILL $BACKEND_PID 2>/dev/null
        rm -f "$BACKEND_PID_FILE"
    fi
    
    # Beende Bot
    if [ -f "$BOT_PID_FILE" ]; then
        BOT_PID=$(cat "$BOT_PID_FILE")
        echo -e "${CYAN}📋 Beende Bot PID: $BOT_PID${NC}"
        kill -TERM $BOT_PID 2>/dev/null
        sleep 2
        kill -KILL $BOT_PID 2>/dev/null
        rm -f "$BOT_PID_FILE"
    fi
    
    echo -e "${GREEN}✅ Alle Services beendet${NC}"
    exit 0
}

# Signal Handler für sauberes Beenden
trap cleanup SIGINT SIGTERM

# Prüfe Verzeichnisse
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Backend-Verzeichnis nicht gefunden${NC}"
    exit 1
fi

if [ ! -d "bot" ]; then
    echo -e "${RED}❌ Bot-Verzeichnis nicht gefunden${NC}"
    exit 1
fi

if [ ! -d "webui" ]; then
    echo -e "${RED}❌ WebUI-Verzeichnis nicht gefunden${NC}"
    exit 1
fi

# Prüfe ob zentrale Virtual Environment existiert
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️ Zentrale Virtual Environment nicht gefunden. Erstelle neues venv...${NC}"
    python3 -m venv venv
    echo -e "${BLUE}📦 Installiere zentrale Dependencies...${NC}"
    source venv/bin/activate
    pip install -r requirements.txt
    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
    fi
    if [ -f "bot/requirements.txt" ]; then
        pip install -r bot/requirements.txt
    fi
    if [ -f "userbot_service/requirements.txt" ]; then
        pip install -r userbot_service/requirements.txt
    fi
else
    # Aktiviere zentrale Virtual Environment
    echo -e "${BLUE}🔧 Aktiviere zentrale Virtual Environment...${NC}"
source venv/bin/activate
fi

# Prüfe Python-Version
echo -e "${CYAN}🐍 Python-Version:${NC}"
python --version

# Prüfe installierte Pakete
echo -e "${CYAN}📦 Installierte Pakete:${NC}"
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|requests|pyrogram|tgcrypto)"

# Hole externe IP-Adresse
EXTERNAL_IP=$(curl -4 -s ifconfig.me 2>/dev/null || curl -4 -s ipinfo.io/ip 2>/dev/null || echo "unbekannt")
echo -e "${CYAN}🌐 Externe IP: $EXTERNAL_IP${NC}"

# Setze externe URLs für interne Tests
export BACKEND_URL="http://$EXTERNAL_IP:8000"
export WEBUI_URL="http://$EXTERNAL_IP"

# Setze korrekte HTTPS-Domains für Bot (Telegram WebApp erfordert HTTPS)
export BOT_BACKEND_URL="https://api.bit-team-bot.online"
export BOT_WEBUI_URL="https://webui.bit-team-bot.online"

echo -e "${CYAN}🌍 Konfigurierte URLs:${NC}"
echo "   🔗 Backend URL (Tests): $BACKEND_URL"
echo "   🌐 WebUI URL (Tests): $WEBUI_URL"
echo "   🔗 Backend URL (Bot): $BOT_BACKEND_URL"
echo "   🌐 WebUI URL (Bot): $BOT_WEBUI_URL"
echo ""

# ===== WEBUI STATUS PRÜFEN =====
echo -e "${BLUE}🌐 Prüfe WebUI-Status...${NC}"

# Nginx Status
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx läuft${NC}"
else
    echo -e "${RED}❌ Nginx läuft nicht${NC}"
    echo -e "${YELLOW}⚠️ Starte Nginx...${NC}"
    sudo systemctl start nginx
fi

# Teste WebUI-Erreichbarkeit
if curl -s --connect-timeout 5 "http://localhost" > /dev/null; then
    echo -e "${GREEN}✅ WebUI lokal erreichbar${NC}"
else
    echo -e "${RED}❌ WebUI lokal nicht erreichbar${NC}"
fi

# ===== BACKEND STARTEN =====
echo -e "${BLUE}📡 Starte Backend...${NC}"
cd backend

# Prüfe Backend-Konfiguration
echo -e "${CYAN}⚙️ Backend-Konfiguration:${NC}"
if [ -f "app/config.py" ]; then
    echo -e "${GREEN}✅ app/config.py gefunden${NC}"
else
    echo -e "${RED}❌ app/config.py nicht gefunden${NC}"
fi

# Prüfe Datenbank
if [ -f "telegram_bot.db" ]; then
    echo -e "${GREEN}✅ telegram_bot.db gefunden${NC}"
else
    echo -e "${YELLOW}⚠️ telegram_bot.db nicht gefunden${NC}"
fi

# Starte Backend
echo -e "${BLUE}🚀 Starte Backend mit Debug-Logging...${NC}"
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log \
    --use-colors \
    --forwarded-allow-ips="*" \
    --proxy-headers 2>&1 | tee "../$BACKEND_LOG" &
BACKEND_PID=$!

# Speichere Backend PID
echo $BACKEND_PID > "../$BACKEND_PID_FILE"
cd ..

echo -e "${GREEN}✅ Backend gestartet mit PID: $BACKEND_PID${NC}"

# Warte auf Backend-Start
echo -e "${YELLOW}⏳ Warte auf Backend-Start...${NC}"
sleep 10

# Teste Backend-Verbindung
echo -e "${CYAN}🔗 Teste Backend-Verbindung...${NC}"
if curl -s --connect-timeout 10 "$BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend erreichbar unter: $BACKEND_URL${NC}"
else
    echo -e "${RED}❌ Backend nicht erreichbar unter: $BACKEND_URL${NC}"
    echo -e "${YELLOW}⚠️ Backend-Start fehlgeschlagen${NC}"
fi

# ===== BOT STARTEN =====
echo -e "${BLUE}🤖 Starte Bot...${NC}"
cd bot

# Prüfe Bot-Konfiguration
echo -e "${CYAN}⚙️ Bot-Konfiguration:${NC}"
if [ -f "config.py" ]; then
    echo -e "${GREEN}✅ config.py gefunden${NC}"
else
    echo -e "${RED}❌ config.py nicht gefunden${NC}"
fi

# Prüfe Session-Datei
if [ -f "bitteam-bot.session" ]; then
    echo -e "${GREEN}✅ bitteam-bot.session gefunden${NC}"
else
    echo -e "${YELLOW}⚠️ bitteam-bot.session nicht gefunden (wird beim ersten Start erstellt)${NC}"
fi

# Setze Debug-Umgebungsvariablen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYROGRAM_LOG_LEVEL="DEBUG"
export PYTHONUNBUFFERED=1

# Setze Bot-spezifische URLs für Telegram WebApp (muss HTTPS sein)
export BACKEND_URL="$BOT_BACKEND_URL"
export WEBUI_URL="$BOT_WEBUI_URL"

# Starte Bot
echo -e "${BLUE}🚀 Starte Bot mit Debug-Logging...${NC}"
python -u bot.py 2>&1 | tee "../$BOT_LOG" &
BOT_PID=$!

# Speichere Bot PID
echo $BOT_PID > "../$BOT_PID_FILE"
cd ..

echo -e "${GREEN}✅ Bot gestartet mit PID: $BOT_PID${NC}"

# ===== WEBUI DEBUG STARTEN =====
echo -e "${BLUE}🌐 Starte WebUI Debug-Modus...${NC}"

# Erstelle WebUI Log-Datei
touch "$WEBUI_LOG"

# Funktion zum Loggen
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$WEBUI_LOG"
}

log_message "🚀 Komplett-Debug gestartet"

# Teste alle Services
echo -e "${CYAN}🔗 Teste alle Services...${NC}"
log_message "Teste alle Services"

# Backend Test (lokale IPv6 für Tests)
if curl -s --connect-timeout 5 "http://$EXTERNAL_IP:8000/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend (lokal): http://$EXTERNAL_IP:8000${NC}"
    log_message "✅ Backend lokal erreichbar"
else
    echo -e "${RED}❌ Backend (lokal): http://$EXTERNAL_IP:8000${NC}"
    log_message "❌ Backend lokal nicht erreichbar"
fi

# Backend Test (HTTPS Domain)
if curl -s --connect-timeout 5 "$BOT_BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend (HTTPS): $BOT_BACKEND_URL${NC}"
    log_message "✅ Backend HTTPS erreichbar"
else
    echo -e "${RED}❌ Backend (HTTPS): $BOT_BACKEND_URL${NC}"
    log_message "❌ Backend HTTPS nicht erreichbar"
fi

# WebUI Test
if curl -s --connect-timeout 5 "http://localhost" > /dev/null; then
    echo -e "${GREEN}✅ WebUI: http://localhost${NC}"
    log_message "✅ WebUI lokal erreichbar"
else
    echo -e "${RED}❌ WebUI: http://localhost${NC}"
    log_message "❌ WebUI lokal nicht erreichbar"
fi

# Domain Test (HTTPS)
if curl -s --connect-timeout 5 "$BOT_WEBUI_URL" > /dev/null; then
    echo -e "${GREEN}✅ WebUI Domain: $BOT_WEBUI_URL${NC}"
    log_message "✅ WebUI Domain erreichbar"
else
    echo -e "${RED}❌ WebUI Domain: $BOT_WEBUI_URL${NC}"
    log_message "❌ WebUI Domain nicht erreichbar"
fi

# ===== STATUS ANZEIGEN =====
echo ""
echo -e "${GREEN}✅ Alle Services erfolgreich gestartet!${NC}"
echo -e "${CYAN}📊 Service-Status:${NC}"
echo "   📡 Backend (lokal): http://$EXTERNAL_IP:8000 (PID: $BACKEND_PID)"
echo "   📡 Backend (HTTPS): $BOT_BACKEND_URL"
echo "   🤖 Bot: Läuft (PID: $BOT_PID)"
echo "   🌐 WebUI (lokal): http://localhost"
echo "   🌐 WebUI (HTTPS): $BOT_WEBUI_URL"
echo "   📚 API Docs: $BOT_BACKEND_URL/docs"
echo "   🔍 Health Check: $BOT_BACKEND_URL/health"
echo "   📝 Backend Log: $BACKEND_LOG"
echo "   📝 Bot Log: $BOT_LOG"
echo "   📝 WebUI Log: $WEBUI_LOG"
echo ""
echo -e "${YELLOW}⚠️ WICHTIG: Stelle sicher, dass die Firewall-Ports freigegeben sind!${NC}"
echo -e "${YELLOW}   Backend: sudo ufw allow 8000${NC}"
echo -e "${YELLOW}   WebUI: sudo ufw allow 80${NC}"
echo ""
echo -e "${CYAN}📋 Live-Logs werden in Echtzeit angezeigt...${NC}"
echo -e "${CYAN}Drücke Ctrl+C zum Beenden...${NC}"
echo ""

log_message "Live-Monitoring gestartet"

# Warte auf Bot-Start
sleep 5

# Zeige aktuelle Logs
echo -e "${GREEN}📋 Letzte Backend-Logs:${NC}"
if [ -f "$BACKEND_LOG" ]; then
    tail -5 "$BACKEND_LOG"
fi

echo ""
echo -e "${GREEN}📋 Letzte Bot-Logs:${NC}"
if [ -f "$BOT_LOG" ]; then
    tail -5 "$BOT_LOG"
fi

echo ""
echo -e "${GREEN}📋 Letzte Nginx-Logs:${NC}"
sudo tail -5 /var/log/nginx/access.log 2>/dev/null || echo "Keine Nginx-Logs verfügbar"

echo ""
echo -e "${YELLOW}📋 Live-Logs (Echtzeit):${NC}"

# Starte Live-Log-Überwachung
(
    # Überwache Backend Log
    tail -f "$BACKEND_LOG" 2>/dev/null | while read line; do
        echo -e "${BLUE}[BACKEND]${NC} $line"
    done &
    
    # Überwache Bot Log
    tail -f "$BOT_LOG" 2>/dev/null | while read line; do
        echo -e "${GREEN}[BOT]${NC} $line"
    done &
    
    # Überwache Nginx Access Log
    sudo tail -f /var/log/nginx/access.log 2>/dev/null | while read line; do
        echo -e "${PURPLE}[NGINX-ACCESS]${NC} $line" | tee -a "$WEBUI_LOG"
    done &
    
    # Überwache Nginx Error Log
    sudo tail -f /var/log/nginx/error.log 2>/dev/null | while read line; do
        echo -e "${RED}[NGINX-ERROR]${NC} $line" | tee -a "$WEBUI_LOG"
    done &
    
    wait
) &

# Warten auf Beendigung
wait 