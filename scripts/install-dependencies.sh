#!/bin/bash

# Farben für die Ausgabe
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funktion für Fehlerbehandlung
handle_error() {
    echo -e "${RED}[✗] Fehler: $1${NC}"
    exit 1
}

# Überprüfe Python-Installation
if ! command -v python3 &> /dev/null; then
    handle_error "Python3 ist nicht installiert"
fi

# Überprüfe pip-Installation
if ! command -v pip3 &> /dev/null; then
    handle_error "pip3 ist nicht installiert"
fi

# Überprüfe npm-Installation
if ! command -v npm &> /dev/null; then
    handle_error "npm ist nicht installiert"
fi

# Lösche alte virtuelle Umgebung, falls vorhanden
if [ -d "venv" ]; then
    echo -e "${YELLOW}[!] Lösche alte virtuelle Umgebung...${NC}"
    rm -rf venv
fi

echo -e "${GREEN}[✓] Erstelle virtuelle Python-Umgebung...${NC}"
python3 -m venv venv || handle_error "Fehler beim Erstellen der virtuellen Umgebung"

echo -e "${GREEN}[✓] Aktiviere virtuelle Umgebung...${NC}"
source venv/bin/activate || handle_error "Fehler beim Aktivieren der virtuellen Umgebung"

echo -e "${GREEN}[✓] Aktualisiere pip...${NC}"
./venv/bin/pip install --upgrade pip || handle_error "Fehler beim Aktualisieren von pip"

echo -e "${GREEN}[✓] Installiere Backend-Abhängigkeiten...${NC}"
if [ -f "backend/requirements.txt" ]; then
    ./venv/bin/pip install -r backend/requirements.txt || handle_error "Fehler beim Installieren der Backend-Abhängigkeiten"
else
    handle_error "backend/requirements.txt nicht gefunden"
fi

echo -e "${GREEN}[✓] Installiere Userbot-Service-Abhängigkeiten...${NC}"
if [ -f "userbot_service/requirements.txt" ]; then
    ./venv/bin/pip install -r userbot_service/requirements.txt || handle_error "Fehler beim Installieren der Userbot-Service-Abhängigkeiten"
else
    handle_error "userbot_service/requirements.txt nicht gefunden"
fi

echo -e "${GREEN}[✓] Installiere Frontend-Abhängigkeiten...${NC}"
if [ -d "webui" ]; then
    cd webui && npm install || handle_error "Fehler beim Installieren der Frontend-Abhängigkeiten"
    cd ..
else
    handle_error "webui Verzeichnis nicht gefunden"
fi

echo -e "${GREEN}[✓] Alle Abhängigkeiten wurden erfolgreich installiert${NC}" 