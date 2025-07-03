#!/bin/bash

# Telegram Bot Management System - Dependency Checker
# Prüft alle Dependencies und stellt sicherstellt, dass nichts fehlt

echo "🔍 Prüfe alle Dependencies für Bit-Team-Bot..."

# Farben für bessere Lesbarkeit
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Prüfe ob zentrale venv existiert
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Zentrale Virtual Environment nicht gefunden${NC}"
    echo -e "${YELLOW}💡 Führe zuerst aus: ./setup_central_venv.sh${NC}"
    exit 1
fi

# Aktiviere zentrale Virtual Environment
echo -e "${BLUE}🔧 Aktiviere zentrale Virtual Environment...${NC}"
source venv/bin/activate

# Prüfe Python-Version
echo -e "${CYAN}🐍 Python-Version:${NC}"
python --version

# Liste aller benötigten Module
declare -a REQUIRED_MODULES=(
    # Web Framework & API
    "fastapi"
    "uvicorn"
    "starlette"
    "pydantic"
    "pydantic_settings"
    "multipart"
    
    # Database & ORM
    "sqlalchemy"
    "databases"
    "alembic"
    
    # Authentication & Security
    "jose"
    "passlib"
    "jwt"
    "bcrypt"
    
    # Telegram Libraries
    "aiogram"
    "telethon"
    "pyrogram"
    "tgcrypto"
    
    # HTTP & Networking
    "requests"
    "httpx"
    "aiohttp"
    
    # Payment & Blockchain
    "web3"
    "stripe"
    
    # File Handling
    "aiofiles"
    
    # Logging & Monitoring
    "loguru"
    
    # Utilities
    "dotenv"
    "deep_translator"
    
    # Development & Testing
    "pytest"
    "pytest_asyncio"
    "black"
    "flake8"
    "mypy"
)

# Prüfe jedes Modul
echo -e "${BLUE}🔍 Prüfe alle Module...${NC}"
MISSING_MODULES=()
INSTALLED_MODULES=()

for module in "${REQUIRED_MODULES[@]}"; do
    case $module in
        "pydantic_settings")
            if python -c "import pydantic_settings" 2>/dev/null; then
                echo -e "${GREEN}✅ pydantic-settings${NC}"
                INSTALLED_MODULES+=("pydantic-settings")
            else
                echo -e "${RED}❌ pydantic-settings fehlt${NC}"
                MISSING_MODULES+=("pydantic-settings")
            fi
            ;;
        "multipart")
            if python -c "import multipart" 2>/dev/null; then
                echo -e "${GREEN}✅ python-multipart${NC}"
                INSTALLED_MODULES+=("python-multipart")
            else
                echo -e "${RED}❌ python-multipart fehlt${NC}"
                MISSING_MODULES+=("python-multipart")
            fi
            ;;
        "jose")
            if python -c "import jose" 2>/dev/null; then
                echo -e "${GREEN}✅ python-jose${NC}"
                INSTALLED_MODULES+=("python-jose")
            else
                echo -e "${RED}❌ python-jose fehlt${NC}"
                MISSING_MODULES+=("python-jose")
            fi
            ;;
        "jwt")
            if python -c "import jwt" 2>/dev/null; then
                echo -e "${GREEN}✅ PyJWT${NC}"
                INSTALLED_MODULES+=("PyJWT")
            else
                echo -e "${RED}❌ PyJWT fehlt${NC}"
                MISSING_MODULES+=("PyJWT")
            fi
            ;;
        "dotenv")
            if python -c "import dotenv" 2>/dev/null; then
                echo -e "${GREEN}✅ python-dotenv${NC}"
                INSTALLED_MODULES+=("python-dotenv")
            else
                echo -e "${RED}❌ python-dotenv fehlt${NC}"
                MISSING_MODULES+=("python-dotenv")
            fi
            ;;
        "deep_translator")
            if python -c "import deep_translator" 2>/dev/null; then
                echo -e "${GREEN}✅ deep-translator${NC}"
                INSTALLED_MODULES+=("deep-translator")
            else
                echo -e "${RED}❌ deep-translator fehlt${NC}"
                MISSING_MODULES+=("deep-translator")
            fi
            ;;
        "pytest_asyncio")
            if python -c "import pytest_asyncio" 2>/dev/null; then
                echo -e "${GREEN}✅ pytest-asyncio${NC}"
                INSTALLED_MODULES+=("pytest-asyncio")
            else
                echo -e "${RED}❌ pytest-asyncio fehlt${NC}"
                MISSING_MODULES+=("pytest-asyncio")
            fi
            ;;
        *)
            if python -c "import $module" 2>/dev/null; then
                echo -e "${GREEN}✅ $module${NC}"
                INSTALLED_MODULES+=("$module")
            else
                echo -e "${RED}❌ $module fehlt${NC}"
                MISSING_MODULES+=("$module")
            fi
            ;;
    esac
done

# Zeige Zusammenfassung
echo ""
echo -e "${CYAN}📊 Dependency Check Zusammenfassung:${NC}"
echo -e "${GREEN}✅ Installiert: ${#INSTALLED_MODULES[@]} Module${NC}"
echo -e "${RED}❌ Fehlend: ${#MISSING_MODULES[@]} Module${NC}"

# Falls Module fehlen, installiere sie
if [ ${#MISSING_MODULES[@]} -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️ Fehlende Module gefunden. Installiere sie...${NC}"
    
    # Upgrade pip zuerst
    echo -e "${BLUE}📦 Upgrade pip...${NC}"
    pip install --upgrade pip
    
    # Installiere alle fehlenden Module
    for module in "${MISSING_MODULES[@]}"; do
        echo -e "${BLUE}📦 Installiere $module...${NC}"
        case $module in
            "python-jose")
                pip install "python-jose[cryptography]==3.3.0"
                ;;
            "python-dotenv")
                pip install "python-dotenv==1.0.1"
                ;;
            "deep-translator")
                pip install "deep-translator==1.11.4"
                ;;
            "pytest-asyncio")
                pip install "pytest-asyncio==0.23.5"
                ;;
            "pydantic-settings")
                pip install "pydantic-settings==2.2.1"
                ;;
            "python-multipart")
                pip install "python-multipart==0.0.9"
                ;;
            "PyJWT")
                pip install "PyJWT==2.8.0"
                ;;
            *)
                pip install "$module"
                ;;
        esac
    done
    
    echo ""
    echo -e "${GREEN}✅ Alle fehlenden Module installiert!${NC}"
fi

# Prüfe spezifische Versionen
echo ""
echo -e "${BLUE}🔍 Prüfe spezifische Versionen...${NC}"

# Wichtige Module mit Versionen
declare -A VERSION_CHECKS=(
    ["fastapi"]="0.111.0"
    ["uvicorn"]="0.30.1"
    ["pyrogram"]="2.0.106"
    ["telethon"]="1.34.0"
    ["sqlalchemy"]="2.0.30"
    ["pydantic"]="2.5.3"
)

for module in "${!VERSION_CHECKS[@]}"; do
    if python -c "import $module; print($module.__version__)" 2>/dev/null; then
        VERSION=$(python -c "import $module; print($module.__version__)" 2>/dev/null)
        EXPECTED_VERSION=${VERSION_CHECKS[$module]}
        if [ "$VERSION" = "$EXPECTED_VERSION" ]; then
            echo -e "${GREEN}✅ $module $VERSION${NC}"
        else
            echo -e "${YELLOW}⚠️ $module $VERSION (erwartet: $EXPECTED_VERSION)${NC}"
        fi
    else
        echo -e "${RED}❌ $module nicht verfügbar${NC}"
    fi
done

# Spezielle Prüfung für tgcrypto
if python -c "import tgcrypto" 2>/dev/null; then
    echo -e "${GREEN}✅ tgcrypto verfügbar${NC}"
else
    echo -e "${RED}❌ tgcrypto nicht verfügbar${NC}"
fi

# Prüfe Service-spezifische Dependencies
echo ""
echo -e "${BLUE}🔍 Prüfe Service-spezifische Dependencies...${NC}"

# Backend Dependencies
echo -e "${CYAN}📡 Backend Dependencies:${NC}"
BACKEND_MODULES=("fastapi" "uvicorn" "sqlalchemy" "pydantic" "jose" "passlib" "jwt")
for module in "${BACKEND_MODULES[@]}"; do
    case $module in
        "jose")
            if python -c "import jose" 2>/dev/null; then
                echo -e "${GREEN}  ✅ python-jose${NC}"
            else
                echo -e "${RED}  ❌ python-jose${NC}"
            fi
            ;;
        "jwt")
            if python -c "import jwt" 2>/dev/null; then
                echo -e "${GREEN}  ✅ PyJWT${NC}"
            else
                echo -e "${RED}  ❌ PyJWT${NC}"
            fi
            ;;
        *)
            if python -c "import $module" 2>/dev/null; then
                echo -e "${GREEN}  ✅ $module${NC}"
            else
                echo -e "${RED}  ❌ $module${NC}"
            fi
            ;;
    esac
done

# Bot Dependencies
echo -e "${CYAN}🤖 Bot Dependencies:${NC}"
BOT_MODULES=("pyrogram" "tgcrypto" "aiogram" "telethon" "requests" "aiohttp")
for module in "${BOT_MODULES[@]}"; do
    if python -c "import $module" 2>/dev/null; then
        echo -e "${GREEN}  ✅ $module${NC}"
    else
        echo -e "${RED}  ❌ $module${NC}"
    fi
done

# Userbot Service Dependencies
echo -e "${CYAN}👤 Userbot Service Dependencies:${NC}"
USERBOT_MODULES=("telethon" "fastapi" "uvicorn" "dotenv" "pydantic" "httpx")
for module in "${USERBOT_MODULES[@]}"; do
    case $module in
        "dotenv")
            if python -c "import dotenv" 2>/dev/null; then
                echo -e "${GREEN}  ✅ python-dotenv${NC}"
            else
                echo -e "${RED}  ❌ python-dotenv${NC}"
            fi
            ;;
        *)
            if python -c "import $module" 2>/dev/null; then
                echo -e "${GREEN}  ✅ $module${NC}"
            else
                echo -e "${RED}  ❌ $module${NC}"
            fi
            ;;
    esac
done

# Zeige alle installierten Pakete (mit cat um Pipe-Fehler zu vermeiden)
echo ""
echo -e "${CYAN}📦 Alle installierten Pakete:${NC}"
pip list | grep -E "(fastapi|uvicorn|sqlalchemy|requests|pyrogram|tgcrypto|telethon|aiogram|pydantic|jose|passlib|jwt|web3|stripe|loguru|dotenv)" | cat

echo ""
echo -e "${GREEN}✅ Dependency Check abgeschlossen!${NC}"
echo -e "${CYAN}📋 Nächste Schritte:${NC}"
echo "   🚀 Debug starten: ./start_all_services_debug.sh"
echo "   🔧 Backend: ./start_backend_debug.sh"
echo "   🤖 Bot: ./start_bot_debug.sh"
echo "   🌐 WebUI: ./start_webui_debug.sh" 