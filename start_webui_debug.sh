#!/bin/bash

# Telegram Bot Management System - WebUI Debug Starter
# Überwacht Nginx-Logs und WebUI-Performance

echo "🌐 Starte WebUI Debug-Modus mit vollständigem Logging..."

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log-Dateien
WEBUI_LOG="webui_debug.log"
NGINX_ACCESS_LOG="/var/log/nginx/access.log"
NGINX_ERROR_LOG="/var/log/nginx/error.log"
WEBUI_ACCESS_LOG="/var/log/nginx/userbot-service.access.log"
WEBUI_ERROR_LOG="/var/log/nginx/userbot-service.error.log"

# Funktion zum Beenden des Debug-Modus
cleanup() {
    echo -e "${YELLOW}🛑 Beende WebUI Debug-Modus...${NC}"
    echo -e "${GREEN}✅ WebUI Debug beendet${NC}"
    exit 0
}

# Signal Handler für sauberes Beenden
trap cleanup SIGINT SIGTERM

# Prüfe ob WebUI-Verzeichnis existiert
if [ ! -d "webui" ]; then
    echo -e "${RED}❌ WebUI-Verzeichnis nicht gefunden${NC}"
    exit 1
fi

# Prüfe ob dist-Verzeichnis existiert
if [ ! -d "webui/dist" ]; then
    echo -e "${RED}❌ webui/dist Verzeichnis nicht gefunden${NC}"
    exit 1
fi

# Hole externe IP-Adresse
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "unbekannt")
echo -e "${CYAN}🌐 Externe IP: $EXTERNAL_IP${NC}"

# ===== SYSTEM STATUS =====
echo -e "${BLUE}🔍 System-Status prüfen...${NC}"

# Nginx Status
echo -e "${CYAN}📡 Nginx-Status:${NC}"
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✅ Nginx läuft${NC}"
    sudo systemctl status nginx --no-pager -l | head -10
else
    echo -e "${RED}❌ Nginx läuft nicht${NC}"
fi

# Nginx Konfiguration
echo -e "${CYAN}⚙️ Nginx-Konfiguration:${NC}"
if [ -f "/etc/nginx/sites-available/webui.conf" ]; then
    echo -e "${GREEN}✅ webui.conf gefunden${NC}"
    echo -e "${CYAN}📋 WebUI Nginx-Konfiguration:${NC}"
    sudo cat /etc/nginx/sites-available/webui.conf
else
    echo -e "${RED}❌ webui.conf nicht gefunden${NC}"
fi

# WebUI Dist-Verzeichnis
echo -e "${CYAN}📁 WebUI Dist-Verzeichnis:${NC}"
ls -la webui/dist/
echo ""

# ===== LOG-ÜBERWACHUNG =====
echo -e "${BLUE}📋 Starte Log-Überwachung...${NC}"

# Erstelle Log-Datei
touch "$WEBUI_LOG"

# Funktion zum Loggen
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$WEBUI_LOG"
}

log_message "🚀 WebUI Debug gestartet"

# Teste WebUI-Erreichbarkeit
echo -e "${CYAN}🔗 Teste WebUI-Erreichbarkeit...${NC}"
log_message "Teste WebUI-Erreichbarkeit"

# Lokaler Test
if curl -s --connect-timeout 5 "http://localhost" > /dev/null; then
    echo -e "${GREEN}✅ WebUI lokal erreichbar${NC}"
    log_message "✅ WebUI lokal erreichbar"
else
    echo -e "${RED}❌ WebUI lokal nicht erreichbar${NC}"
    log_message "❌ WebUI lokal nicht erreichbar"
fi

# Externer Test
if curl -s --connect-timeout 5 "http://$EXTERNAL_IP" > /dev/null; then
    echo -e "${GREEN}✅ WebUI extern erreichbar${NC}"
    log_message "✅ WebUI extern erreichbar"
else
    echo -e "${RED}❌ WebUI extern nicht erreichbar${NC}"
    log_message "❌ WebUI extern nicht erreichbar"
fi

# Domain Test
if curl -s --connect-timeout 5 "http://webui.bit-team-bot.online" > /dev/null; then
    echo -e "${GREEN}✅ WebUI Domain erreichbar${NC}"
    log_message "✅ WebUI Domain erreichbar"
else
    echo -e "${RED}❌ WebUI Domain nicht erreichbar${NC}"
    log_message "❌ WebUI Domain nicht erreichbar"
fi

# ===== LIVE-LOG-ÜBERWACHUNG =====
echo -e "${BLUE}📋 Starte Live-Log-Überwachung...${NC}"
log_message "Starte Live-Log-Überwachung"

# Zeige aktuelle Logs
echo -e "${GREEN}📋 Aktuelle Nginx-Logs:${NC}"
if [ -f "$NGINX_ACCESS_LOG" ]; then
    echo -e "${CYAN}📊 Nginx Access Log (letzte 10 Einträge):${NC}"
    sudo tail -10 "$NGINX_ACCESS_LOG"
fi

if [ -f "$NGINX_ERROR_LOG" ]; then
    echo -e "${CYAN}❌ Nginx Error Log (letzte 10 Einträge):${NC}"
    sudo tail -10 "$NGINX_ERROR_LOG"
fi

if [ -f "$WEBUI_ACCESS_LOG" ]; then
    echo -e "${CYAN}📊 WebUI Access Log (letzte 10 Einträge):${NC}"
    sudo tail -10 "$WEBUI_ACCESS_LOG"
fi

if [ -f "$WEBUI_ERROR_LOG" ]; then
    echo -e "${CYAN}❌ WebUI Error Log (letzte 10 Einträge):${NC}"
    sudo tail -10 "$WEBUI_ERROR_LOG"
fi

# ===== NETZWERK-STATUS =====
echo -e "${BLUE}🌐 Netzwerk-Status:${NC}"
log_message "Prüfe Netzwerk-Status"

# Port-Status
echo -e "${CYAN}🔌 Port-Status:${NC}"
netstat -tlnp | grep -E ":80|:443|:8080" || echo "Keine relevanten Ports gefunden"

# Firewall-Status
echo -e "${CYAN}🔥 Firewall-Status:${NC}"
sudo ufw status

# ===== WEBUI-DEBUG-INFO =====
echo -e "${BLUE}🔧 WebUI-Debug-Informationen:${NC}"
log_message "Sammle WebUI-Debug-Informationen"

# Prüfe WebUI-Dateien
echo -e "${CYAN}📁 WebUI-Dateien:${NC}"
find webui/dist -name "*.html" -o -name "*.js" -o -name "*.css" | head -10

# Prüfe WebUI-Konfiguration
echo -e "${CYAN}⚙️ WebUI-Konfiguration:${NC}"
if [ -f "webui/vite.config.js" ]; then
    echo -e "${GREEN}✅ vite.config.js gefunden${NC}"
    cat webui/vite.config.js
else
    echo -e "${RED}❌ vite.config.js nicht gefunden${NC}"
fi

# ===== LIVE-MONITORING =====
echo ""
echo -e "${GREEN}✅ WebUI Debug-Modus aktiv${NC}"
echo -e "${CYAN}📊 Service-Status:${NC}"
echo "   🌐 WebUI: http://$EXTERNAL_IP"
echo "   🌐 WebUI: http://webui.bit-team-bot.online"
echo "   📝 Debug Log: $WEBUI_LOG"
echo "   📊 Nginx Access: $NGINX_ACCESS_LOG"
echo "   ❌ Nginx Error: $NGINX_ERROR_LOG"
echo ""
echo -e "${YELLOW}⚠️ WICHTIG: Stelle sicher, dass Port 80 in der Firewall freigegeben ist!${NC}"
echo -e "${YELLOW}   Firewall-Befehl: sudo ufw allow 80${NC}"
echo ""
echo -e "${CYAN}📋 Live-Logs werden in Echtzeit angezeigt...${NC}"
echo -e "${CYAN}Drücke Ctrl+C zum Beenden...${NC}"
echo ""

log_message "Live-Monitoring gestartet"

# Starte Live-Log-Überwachung
(
    # Überwache Nginx Access Log
    sudo tail -f "$NGINX_ACCESS_LOG" 2>/dev/null | while read line; do
        echo -e "${GREEN}[ACCESS]${NC} $line" | tee -a "$WEBUI_LOG"
    done &
    
    # Überwache Nginx Error Log
    sudo tail -f "$NGINX_ERROR_LOG" 2>/dev/null | while read line; do
        echo -e "${RED}[ERROR]${NC} $line" | tee -a "$WEBUI_LOG"
    done &
    
    # Überwache WebUI Access Log
    sudo tail -f "$WEBUI_ACCESS_LOG" 2>/dev/null | while read line; do
        echo -e "${BLUE}[WEBUI-ACCESS]${NC} $line" | tee -a "$WEBUI_LOG"
    done &
    
    # Überwache WebUI Error Log
    sudo tail -f "$WEBUI_ERROR_LOG" 2>/dev/null | while read line; do
        echo -e "${PURPLE}[WEBUI-ERROR]${NC} $line" | tee -a "$WEBUI_LOG"
    done &
    
    wait
) &

# Warten auf Beendigung
wait 