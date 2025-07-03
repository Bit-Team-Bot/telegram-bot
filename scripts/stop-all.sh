#!/bin/bash

# Telegram Bot System - Stop-Skript für alle Services
# Verwendung: ./scripts/stop-all.sh

echo "🛑 Stoppe Telegram Bot System..."

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Funktion zum Stoppen eines Services
stop_service() {
    local service_name=$1
    local pid_file=".${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}🛑 Stoppe $service_name (PID: $pid)...${NC}"
            kill "$pid"
            sleep 2
            
            # Prüfe ob Prozess noch läuft
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Force-Kill $service_name...${NC}"
                kill -9 "$pid"
            fi
            
            echo -e "${GREEN}✅ $service_name gestoppt${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name war bereits gestoppt${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  Keine PID-Datei für $service_name gefunden${NC}"
    fi
}

# Funktion zum Stoppen eines Prozesses auf einem bestimmten Port
kill_port() {
    local port=$1
    local pname=$2
    pids=$(lsof -t -i :$port)
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}🛑 Stoppe $pname auf Port $port (PIDs: $pids)...${NC}"
        kill $pids 2>/dev/null
        sleep 2
        # Falls noch Prozesse laufen, force kill
        pids2=$(lsof -t -i :$port)
        if [ ! -z "$pids2" ]; then
            echo -e "${YELLOW}⚠️  Force-Kill $pname auf Port $port...${NC}"
            kill -9 $pids2 2>/dev/null
        fi
        echo -e "${GREEN}✅ $pname auf Port $port gestoppt${NC}"
    fi
}

# Stoppe alle Services
echo "🔄 Stoppe Services..."

# 1. Frontend
stop_service "frontend"
kill_port 8080 "Frontend"
kill_port 8081 "Frontend"
pkill -f "vite" 2>/dev/null
pkill -f "node" 2>/dev/null

# 2. Telegram Bot
stop_service "bot"
# Suche und stoppe ggf. weitere python-Prozesse mit bot.py
pkill -f "python bot.py" 2>/dev/null

# 3. Userbot Service
stop_service "userbot"
kill_port 9000 "Userbot"
pkill -f "uvicorn main:app --host 0.0.0.0 --port 9000" 2>/dev/null

# 4. Backend
stop_service "backend"
kill_port 8000 "Backend"
pkill -f "uvicorn app.main:app --host 0.0.0.0 --port 8000" 2>/dev/null

echo ""
echo -e "${GREEN}🎉 Alle Services gestoppt!${NC}"
echo ""
echo "📋 Zum Starten: ./scripts/start-all.sh" 