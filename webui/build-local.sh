#!/bin/bash

# Frontend für lokale Entwicklung bauen
# Dieses Skript baut das Frontend mit lokalen API-URLs

echo "🔧 Baue Frontend für lokale Entwicklung..."

# Environment-Variablen für lokale Entwicklung setzen
export VITE_API_URL=http://localhost:8000
export VITE_USERBOT_URL=http://localhost:8001
export VITE_APP_TITLE="Telegram Bot Management System (Local)"

echo "📡 API_URL: $VITE_API_URL"
echo "🤖 USERBOT_URL: $VITE_USERBOT_URL"

# Alte dist-Dateien löschen
echo "🗑️ Lösche alte Build-Dateien..."
rm -rf dist

# Frontend bauen
echo "🏗️ Baue Frontend..."
npm run build

# Prüfe ob Build erfolgreich war
if [ $? -eq 0 ]; then
    echo "✅ Frontend erfolgreich gebaut!"
    echo "📁 Neue Dateien in: dist/"
    echo ""
    echo "🚀 Starte lokalen Server:"
    echo "   cd dist && python3 -m http.server 8080"
    echo ""
    echo "🌐 Oder verwende nginx/apache für den dist-Ordner"
else
    echo "❌ Build fehlgeschlagen!"
    exit 1
fi 