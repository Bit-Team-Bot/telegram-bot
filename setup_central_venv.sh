#!/bin/bash

# Telegram Bot Management System - Zentrale Virtual Environment Setup
# Erstellt und konfiguriert eine zentrale venv für alle Services

echo "🔧 Setup zentrale Virtual Environment für Bit-Team-Bot..."

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Prüfe Python-Version
echo -e "${CYAN}🐍 Prüfe Python-Version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ $PYTHON_VERSION gefunden${NC}"
else
    echo -e "${RED}❌ Python3 nicht gefunden${NC}"
    exit 1
fi

# Prüfe ob venv bereits existiert
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️ Zentrale Virtual Environment existiert bereits${NC}"
    read -p "Möchtest du sie neu erstellen? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}🗑️ Lösche bestehende venv...${NC}"
        rm -rf venv
    else
        echo -e "${GREEN}✅ Verwende bestehende venv${NC}"
        source venv/bin/activate
        echo -e "${CYAN}📦 Aktuelle Pakete:${NC}"
        pip list | head -10 | cat
        exit 0
    fi
fi

# Erstelle zentrale Virtual Environment
echo -e "${BLUE}🔧 Erstelle zentrale Virtual Environment...${NC}"
python3 -m venv venv

# Aktiviere Virtual Environment
echo -e "${BLUE}🔧 Aktiviere Virtual Environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}📦 Upgrade pip...${NC}"
pip install --upgrade pip

# Installiere zentrale Dependencies
echo -e "${BLUE}📦 Installiere zentrale Dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    echo -e "${CYAN}📋 Installiere Root requirements.txt...${NC}"
    pip install -r requirements.txt
else
    echo -e "${YELLOW}⚠️ Root requirements.txt nicht gefunden${NC}"
fi

# Installiere Backend Dependencies
if [ -f "backend/requirements.txt" ]; then
    echo -e "${CYAN}📋 Installiere Backend Dependencies...${NC}"
    pip install -r backend/requirements.txt
else
    echo -e "${YELLOW}⚠️ Backend requirements.txt nicht gefunden${NC}"
fi

# Installiere Bot Dependencies
if [ -f "bot/requirements.txt" ]; then
    echo -e "${CYAN}📋 Installiere Bot Dependencies...${NC}"
    pip install -r bot/requirements.txt
else
    echo -e "${YELLOW}⚠️ Bot requirements.txt nicht gefunden${NC}"
fi

# Installiere Userbot Service Dependencies
if [ -f "userbot_service/requirements.txt" ]; then
    echo -e "${CYAN}📋 Installiere Userbot Service Dependencies...${NC}"
    pip install -r userbot_service/requirements.txt
else
    echo -e "${YELLOW}⚠️ Userbot Service requirements.txt nicht gefunden${NC}"
fi

# Zeige installierte Pakete
echo -e "${GREEN}✅ Zentrale Virtual Environment Setup abgeschlossen!${NC}"
echo -e "${CYAN}📦 Installierte Pakete:${NC}"
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|requests|pyrogram|tgcrypto|telethon|aiogram|pydantic|jose|passlib|jwt|web3|stripe|loguru|dotenv)" | cat

# Erstelle .gitignore Eintrag
if [ ! -f ".gitignore" ]; then
    echo -e "${BLUE}📝 Erstelle .gitignore...${NC}"
    touch .gitignore
fi

# Füge venv zu .gitignore hinzu falls nicht vorhanden
if ! grep -q "venv/" .gitignore; then
    echo -e "${BLUE}📝 Füge venv/ zu .gitignore hinzu...${NC}"
    echo "venv/" >> .gitignore
fi

# Erstelle Aktivierungsskript
echo -e "${BLUE}📝 Erstelle Aktivierungsskript...${NC}"
cat > activate_venv.sh << 'EOF'
#!/bin/bash
# Aktivierungsskript für zentrale Virtual Environment
echo "🔧 Aktiviere zentrale Virtual Environment..."
source venv/bin/activate
echo "✅ Virtual Environment aktiviert"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"
echo ""
echo "Verfügbare Services:"
echo "  🔧 Backend: cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo "  🤖 Bot: cd bot && python bot.py"
echo "  👤 Userbot: cd userbot_service && python main.py"
echo ""
echo "Debug-Skripte:"
echo "  🚀 Alle Services: ./start_all_services_debug.sh"
echo "  🔧 Backend: ./start_backend_debug.sh"
echo "  🤖 Bot: ./start_bot_debug.sh"
echo "  🌐 WebUI: ./start_webui_debug.sh"
EOF

chmod +x activate_venv.sh

echo ""
echo -e "${GREEN}✅ Setup abgeschlossen!${NC}"
echo -e "${CYAN}📋 Nächste Schritte:${NC}"
echo "   🔧 Virtual Environment aktivieren: source venv/bin/activate"
echo "   🚀 Oder: ./activate_venv.sh"
echo "   🔧 Debug starten: ./start_all_services_debug.sh"
echo ""
echo -e "${YELLOW}⚠️ Wichtige Hinweise:${NC}"
echo "   - Alle Services verwenden jetzt die zentrale venv"
echo "   - Dependencies werden zentral verwaltet"
echo "   - Einfache Wartung und Updates"
echo "   - Konsistente Python-Umgebung" 