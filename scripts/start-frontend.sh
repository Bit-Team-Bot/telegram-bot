#!/bin/bash
cd "$(dirname "$0")/.."
echo "==> Starte Frontend (Vue.js) ..."

# Prüfe ob Node.js installiert ist
if ! command -v node &> /dev/null; then
    echo "❌ Node.js ist nicht installiert!"
    exit 1
fi

# Prüfe ob npm installiert ist
if ! command -v npm &> /dev/null; then
    echo "❌ npm ist nicht installiert!"
    exit 1
fi

# Wechsle ins Frontend-Verzeichnis
cd webui

# Installiere Dependencies falls node_modules nicht existiert
if [ ! -d "node_modules" ]; then
    echo "📦 Installiere Frontend-Dependencies..."
    npm install
fi

# Starte das Frontend
echo "🚀 Starte Frontend auf Port 8080..."
npm run dev

status=$?
if [ $status -eq 0 ]; then
    echo "✅ Frontend erfolgreich gestartet."
else
    echo "❌ Frontend-Start FEHLGESCHLAGEN!"
fi 