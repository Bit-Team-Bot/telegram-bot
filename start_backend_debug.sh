#!/bin/bash

# Telegram Bot Management System - Backend Debug Starter
# Vollständiges Logging für Problemdiagnose - EXTERNE ERREICHBARKEIT

echo "🔧 Starte Backend im Debug-Modus mit vollständigem Logging (EXTERN ERREICHBAR)..."

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Wechsle ins Projekt-Root (wo dieses Skript liegt)
cd "$(dirname "$0")"

# .env laden (falls vorhanden)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
  echo "✅ .env-Datei erfolgreich geladen."
else
  echo "⚠️  Keine .env-Datei im Projekt-Root gefunden!"
fi

# PYTHONPATH setzen, damit Importe wie 'from app.routes' funktionieren
export PYTHONPATH=$(pwd)

# Log-Datei für Backend
BACKEND_LOG="backend_debug.log"
BACKEND_PID_FILE=".backend_debug.pid"

# Funktion zum Beenden des Backends
cleanup() {
    echo -e "${YELLOW}🛑 Beende Backend...${NC}"
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        echo -e "${CYAN}📋 Beende Prozess PID: $BACKEND_PID${NC}"
        kill -TERM $BACKEND_PID 2>/dev/null
        sleep 2
        kill -KILL $BACKEND_PID 2>/dev/null
        rm -f "$BACKEND_PID_FILE"
    fi
    echo -e "${GREEN}✅ Backend beendet${NC}"
    exit 0
}

# Signal Handler für sauberes Beenden
trap cleanup SIGINT SIGTERM

# Prüfe ob Backend-Verzeichnis existiert
if [ ! -d "backend" ]; then
    echo -e "${RED}❌ Backend-Verzeichnis nicht gefunden${NC}"
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

# Wechsle ins Backend-Verzeichnis
cd backend

# Prüfe Backend-Dependencies
echo -e "${CYAN}🔍 Prüfe Backend-Dependencies...${NC}"
if [ ! -f "requirements.txt" ]; then
    echo -e "${YELLOW}⚠️ requirements.txt nicht gefunden${NC}"
else
    echo -e "${CYAN}📋 Backend requirements.txt gefunden${NC}"
    cat requirements.txt
fi

# Prüfe Backend-Konfiguration
echo -e "${CYAN}⚙️ Backend-Konfiguration:${NC}"
if [ -f "app/config.py" ]; then
    echo -e "${GREEN}✅ app/config.py gefunden${NC}"
else
    echo -e "${RED}❌ app/config.py nicht gefunden${NC}"
fi

# Prüfe Datenbank
echo -e "${CYAN}🗄️ Datenbank-Status:${NC}"
if [ -f "telegram_bot.db" ]; then
    echo -e "${GREEN}✅ telegram_bot.db gefunden${NC}"
    ls -la telegram_bot.db
else
    echo -e "${YELLOW}⚠️ telegram_bot.db nicht gefunden${NC}"
fi

# Prüfe Umgebungsvariablen
echo -e "${CYAN}🌍 Umgebungsvariablen:${NC}"
echo "BACKEND_HOST: ${BACKEND_HOST:-'nicht gesetzt (Standard: 0.0.0.0)'}"
echo "BACKEND_PORT: ${BACKEND_PORT:-'nicht gesetzt (Standard: 8000)'}"
echo "DATABASE_URL: ${DATABASE_URL:-'nicht gesetzt'}"
echo "SECRET_KEY: ${SECRET_KEY:-'nicht gesetzt'}"

# Hole externe IP-Adresse
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unbekannt")
echo -e "${CYAN}🌐 Externe IP: $EXTERNAL_IP${NC}"

# Starte Backend mit vollständigem Debug-Logging - EXTERN ERREICHBAR
echo -e "${BLUE}🚀 Starte Backend mit Debug-Logging (EXTERN ERREICHBAR)...${NC}"
echo -e "${PURPLE}📝 Log-Datei: $BACKEND_LOG${NC}"

# Starte uvicorn mit maximalem Logging und externer Erreichbarkeit
python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --reload \
    --log-level debug \
    --access-log \
    --use-colors \
    --forwarded-allow-ips="*" \
    --proxy-headers 2>&1 | tee "$BACKEND_LOG" &
BACKEND_PID=$!

# Speichere PID
echo $BACKEND_PID > "$BACKEND_PID_FILE"

echo -e "${GREEN}✅ Backend gestartet mit PID: $BACKEND_PID${NC}"
echo -e "${CYAN}📊 Backend-Status:${NC}"
echo "   🔗 Lokale URL: http://localhost:8000"
echo "   🌐 Externe URL: http://$EXTERNAL_IP:8000"
echo "   📚 API Docs: http://$EXTERNAL_IP:8000/docs"
echo "   🔍 Health Check: http://$EXTERNAL_IP:8000/health"
echo "   📝 Log-Datei: $BACKEND_LOG"
echo "   🆔 PID: $BACKEND_PID"
echo ""
echo -e "${YELLOW}⚠️ WICHTIG: Stelle sicher, dass Port 8000 in der Firewall freigegeben ist!${NC}"
echo -e "${YELLOW}   Firewall-Befehl: sudo ufw allow 8000${NC}"
echo ""

# Zeige Logs in Echtzeit
echo -e "${YELLOW}📋 Backend-Logs (Echtzeit):${NC}"
echo -e "${CYAN}Drücke Ctrl+C zum Beenden...${NC}"
echo ""

# Warte auf Backend-Start
sleep 5

# Zeige aktuelle Logs
if [ -f "$BACKEND_LOG" ]; then
    echo -e "${GREEN}📋 Letzte Log-Einträge:${NC}"
    tail -20 "$BACKEND_LOG"
fi

# Warten auf Beendigung
wait 

# Backend als Modul starten (so funktionieren alle Importe)
python3 -m backend.app.main 