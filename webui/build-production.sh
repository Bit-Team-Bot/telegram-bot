#!/bin/bash

# Frontend für Produktion bauen
# Dieses Skript baut das Frontend mit öffentlichen API-URLs

echo "🌐 Baue Frontend für Produktion..."

# Environment-Variablen für Produktion setzen
export VITE_API_URL=https://api.bit-team-bot.online
export VITE_USERBOT_URL=https://userbot.bit-team-bot.online
export VITE_APP_TITLE="Telegram Bot Management System"

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
    echo "✅ Frontend erfolgreich für Produktion gebaut!"
    echo "📁 Neue Dateien in: dist/"
    echo ""
    echo "🚀 Deployment:"
    echo "   Kopiere den dist-Ordner auf deinen Webserver"
    echo "   Oder verwende: rsync -av dist/ user@server:/var/www/html/"
    echo ""
    echo "🔍 Teste die APIs:"
    echo "   node debug-production.js"
else
    echo "❌ Build fehlgeschlagen!"
    exit 1
fi 