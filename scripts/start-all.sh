#!/bin/bash
cd "$(dirname "$0")/.."
# Telegram Bot System - Start-Skript für alle Services
# Verwendung: ./scripts/start-all.sh

set -e

echo "🚀 Starte Telegram Bot System..."

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktion zum Prüfen ob Port verfügbar ist
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}❌ Port $1 ist bereits belegt${NC}"
    exit 1
fi
}

# Funktion zum Starten eines Services
start_service() {
    local service_name=$1
    local service_dir=$2
    local start_cmd=$3
    
    echo -e "${YELLOW}📦 Starte $service_name...${NC}"
    cd "$service_dir"
    
    # Immer zentrale venv im Projekt-Root nutzen!
    if [ -f "../../venv/bin/activate" ]; then
        source ../../venv/bin/activate
    elif [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
    elif [ -f "./venv/bin/activate" ]; then
        source ./venv/bin/activate
    else
        echo -e "${RED}❌ Zentrale Virtual Environment nicht gefunden im Projekt-Root!${NC}"
        echo "Führen Sie zuerst die Installation aus: pip install -r requirements.txt"
        exit 1
    fi

    eval "$start_cmd" &
    local pid=$!
    echo $pid > "../.${service_name}.pid"
    
    echo -e "${GREEN}✅ $service_name gestartet (PID: $pid)${NC}"
    cd ..
}

# Prüfe Ports
echo "🔍 Prüfe verfügbare Ports..."
check_port 8000  # Backend
check_port 9000  # Userbot Service
check_port 8080  # Frontend

# Erstelle PID-Verzeichnis
mkdir -p .pids

# Starte Services
echo ""
echo "🔄 Starte Services..."

# 1. Backend
start_service "backend" "backend" "uvicorn app.main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ../certs/key.pem --ssl-certfile ../certs/cert.pem"

# 2. Userbot Service
start_service "userbot" "userbot_service" "uvicorn main:app --host 0.0.0.0 --port 9000 --ssl-keyfile ../certs/key.pem --ssl-certfile ../certs/cert.pem"

# 3. Telegram Bot
start_service "bot" "bot" "python bot.py"

# 4. Frontend
echo -e "${YELLOW}📦 Starte Frontend...${NC}"
cd webui

# Prüfe ob Node.js installiert ist
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js ist nicht installiert!${NC}"
    exit 1
fi

# Installiere Dependencies falls node_modules nicht existiert
if [ ! -d "node_modules" ]; then
    echo "📦 Installiere Frontend-Dependencies..."
    npm install
fi

npm run dev &
frontend_pid=$!
echo $frontend_pid > "../.frontend.pid"
echo -e "${GREEN}✅ Frontend gestartet (PID: $frontend_pid)${NC}"
cd ..

# Warte kurz und prüfe Status
sleep 3

echo ""
echo -e "${GREEN}🎉 Alle Services gestartet!${NC}"
echo ""
echo "📊 Service-Status:"
echo "  Backend:      https://localhost:8000"
echo "  Userbot:      https://localhost:9000"
echo "  Frontend:     http://localhost:8080"
echo "  API Docs:     https://localhost:8000/docs"
echo ""
echo "🛑 Zum Stoppen: ./scripts/stop-all.sh"
echo "📋 Logs anzeigen: ./scripts/show-logs.sh"
