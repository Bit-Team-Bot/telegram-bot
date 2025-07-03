#!/bin/bash

# Starte die korrekten Cloudflare Tunnels
# Verwendet die bestehende saubere Konfiguration

echo "🚀 Starte korrekte Cloudflare Tunnels..."

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Prüfe ob cloudflared läuft
if pgrep -x "cloudflared" > /dev/null; then
    echo -e "${YELLOW}⚠️ Cloudflared läuft bereits. Stoppe alle Instanzen...${NC}"
    pkill cloudflared
    sleep 2
fi

# Starte bit-team-bot Tunnel (für API und WebUI)
echo -e "${GREEN}🔗 Starte bit-team-bot Tunnel (API + WebUI)...${NC}"
cloudflared tunnel run --config ~/.cloudflared/config-webui.yml &
BIT_TEAM_BOT_PID=$!
echo "Bit-Team-Bot Tunnel PID: $BIT_TEAM_BOT_PID"

# Starte userbot-service Tunnel
echo -e "${GREEN}🤖 Starte userbot-service Tunnel...${NC}"
cloudflared tunnel run userbot-service &
USERBOT_PID=$!
echo "Userbot Tunnel PID: $USERBOT_PID"

# Warte kurz
sleep 5

# Zeige Status
echo ""
echo -e "${GREEN}✅ Tunnels gestartet:${NC}"
echo "   🔗 bit-team-bot: PID $BIT_TEAM_BOT_PID"
echo "   🤖 userbot-service: PID $USERBOT_PID"
echo ""
echo "📋 Verfügbare URLs:"
echo "   🔗 Backend API: https://api.bit-team-bot.online"
echo "   🌐 WebUI: https://webui.bit-team-bot.online"
echo "   🤖 Userbot: https://userbot.bit-team-bot.online"
echo ""
echo "💡 Zum Stoppen: pkill cloudflared" 