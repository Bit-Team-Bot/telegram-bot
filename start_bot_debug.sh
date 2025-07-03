#!/bin/bash

# Telegram Bot Management System - Bot Debug Starter
# Vollständiges Logging für Problemdiagnose - EXTERNE ERREICHBARKEIT

echo "🤖 Starte Telegram Bot im Debug-Modus mit vollständigem Logging (EXTERN ERREICHBAR)..."

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# .env-Datei laden, falls vorhanden
if [ -f .env ]; then
    echo -e "${BLUE}🔧 Lade Umgebungsvariablen aus .env-Datei...${NC}"
    set -a
    source .env
    set +a
    echo -e "${GREEN}✅ .env-Datei erfolgreich geladen.${NC}"
else
    echo -e "${YELLOW}⚠️ .env-Datei nicht gefunden. Skript wird mit Standardeinstellungen fortgesetzt.${NC}"
fi

# Log-Datei für Bot
BOT_LOG="bot_debug.log"
BOT_PID_FILE=".bot_debug.pid"

# Funktion zum Beenden des Bots
cleanup() {
    echo -e "${YELLOW}🛑 Beende Bot...${NC}"
    if [ -f "$BOT_PID_FILE" ]; then
        BOT_PID=$(cat "$BOT_PID_FILE")
        echo -e "${CYAN}📋 Beende Prozess PID: $BOT_PID${NC}"
        kill -TERM $BOT_PID 2>/dev/null
        sleep 2
        kill -KILL $BOT_PID 2>/dev/null
        rm -f "$BOT_PID_FILE"
    fi
    echo -e "${GREEN}✅ Bot beendet${NC}"
    exit 0
}

# Signal Handler für sauberes Beenden
trap cleanup SIGINT SIGTERM

# Prüfe ob Bot-Verzeichnis existiert
if [ ! -d "bot" ]; then
    echo -e "${RED}❌ Bot-Verzeichnis nicht gefunden${NC}"
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
pip list | grep -E "(pyrogram|tgcrypto|requests|asyncio|fastapi|uvicorn)"

# Wechsle ins Bot-Verzeichnis
cd bot

# Prüfe Bot-Dependencies
echo -e "${CYAN}🔍 Prüfe Bot-Dependencies...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}⚠️ requirements.txt nicht gefunden${NC}"
else
    echo -e "${CYAN}📋 Bot requirements.txt gefunden${NC}"
    cat requirements.txt
fi

# Prüfe Bot-Konfiguration
echo -e "${CYAN}⚙️ Bot-Konfiguration:${NC}"
if [ -f "config.py" ]; then
    echo -e "${GREEN}✅ config.py gefunden${NC}"
    echo -e "${CYAN}📋 Bot-Konfiguration:${NC}"
    cat config.py
else
    echo -e "${RED}❌ config.py nicht gefunden${NC}"
fi

# Prüfe Session-Datei
echo -e "${CYAN}🔐 Session-Status:${NC}"
if [ -f "bitteam-bot.session" ]; then
    echo -e "${GREEN}✅ bitteam-bot.session gefunden${NC}"
    ls -la bitteam-bot.session
else
    echo -e "${YELLOW}⚠️ bitteam-bot.session nicht gefunden (wird beim ersten Start erstellt)${NC}"
fi

# Hole externe IP-Adresse
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unbekannt")
echo -e "${CYAN}🌐 Externe IP: $EXTERNAL_IP${NC}"

# Prüfe Umgebungsvariablen
echo -e "${CYAN}🌍 Umgebungsvariablen:${NC}"
echo "API_ID: ${API_ID:-'nicht gesetzt'}"
echo "API_HASH: ${API_HASH:-'nicht gesetzt'}"
echo "BOT_TOKEN: ${BOT_TOKEN:-'nicht gesetzt'}"
echo "BACKEND_URL: ${BACKEND_URL:-'nicht gesetzt'}"
echo "WEBUI_URL: ${WEBUI_URL:-'nicht gesetzt'}"

# Setze externe URLs falls nicht gesetzt
if [ -z "$BACKEND_URL" ]; then
    export BACKEND_URL="http://$EXTERNAL_IP:8000"
    echo -e "${YELLOW}⚠️ BACKEND_URL nicht gesetzt, verwende: $BACKEND_URL${NC}"
fi

if [ -z "$WEBUI_URL" ]; then
    export WEBUI_URL="http://$EXTERNAL_IP:8080"
    echo -e "${YELLOW}⚠️ WEBUI_URL nicht gesetzt, verwende: $WEBUI_URL${NC}"
fi

# Prüfe .env Datei
echo -e "${CYAN}🔐 .env Datei:${NC}"
if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env gefunden${NC}"
    echo -e "${CYAN}📋 .env Inhalt (ohne sensible Daten):${NC}"
    grep -v -E "(API_HASH|BOT_TOKEN)" .env || echo "Keine .env Datei gefunden"
else
    echo -e "${YELLOW}⚠️ .env nicht gefunden${NC}"
fi

# Prüfe bestehende Logs
echo -e "${CYAN}📝 Bestehende Logs:${NC}"
if [ -f "bot.log" ]; then
    echo -e "${GREEN}✅ bot.log gefunden${NC}"
    echo -e "${CYAN}📋 Letzte 10 Log-Einträge:${NC}"
    tail -10 bot.log
else
    echo -e "${YELLOW}⚠️ bot.log nicht gefunden${NC}"
fi

# Teste Backend-Verbindung
echo -e "${CYAN}🔗 Teste Backend-Verbindung...${NC}"
if curl -s --connect-timeout 5 "$BACKEND_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ Backend erreichbar unter: $BACKEND_URL${NC}"
else
    echo -e "${RED}❌ Backend nicht erreichbar unter: $BACKEND_URL${NC}"
    echo -e "${YELLOW}⚠️ Stelle sicher, dass das Backend läuft und Port 8000 freigegeben ist${NC}"
fi

# Starte Bot mit vollständigem Debug-Logging
echo -e "${BLUE}🚀 Starte Bot mit Debug-Logging...${NC}"
echo -e "${PURPLE}📝 Log-Datei: $BOT_LOG${NC}"

# Setze Debug-Umgebungsvariablen
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYROGRAM_LOG_LEVEL="DEBUG"
export PYTHONUNBUFFERED=1

# Starte Bot mit maximalem Logging
python -u bot.py 2>&1 | tee "$BOT_LOG" &
BOT_PID=$!

# Speichere PID
echo $BOT_PID > "$BOT_PID_FILE"

echo -e "${GREEN}✅ Bot gestartet mit PID: $BOT_PID${NC}"
echo -e "${CYAN}📊 Bot-Status:${NC}"
echo "   🤖 Bot: Läuft (Telegram API)"
echo "   📝 Log-Datei: $BOT_LOG"
echo "   🆔 PID: $BOT_PID"
echo "   🔗 Backend URL: $BACKEND_URL"
echo "   🌐 WebUI URL: $WEBUI_URL"
echo ""
echo -e "${YELLOW}⚠️ WICHTIG: Stelle sicher, dass die Firewall-Ports freigegeben sind!${NC}"
echo -e "${YELLOW}   Backend: sudo ufw allow 8000${NC}"
echo -e "${YELLOW}   WebUI: sudo ufw allow 8080${NC}"
echo ""

# Warte auf Bot-Start
sleep 5

# Zeige aktuelle Logs
if [ -f "$BOT_LOG" ]; then
    echo -e "${GREEN}📋 Letzte Log-Einträge:${NC}"
    tail -20 "$BOT_LOG"
fi

# Zeige Logs in Echtzeit
echo -e "${YELLOW}📋 Bot-Logs (Echtzeit):${NC}"
echo -e "${CYAN}Drücke Ctrl+C zum Beenden...${NC}"
echo ""

# Warten auf Beendigung
wait 