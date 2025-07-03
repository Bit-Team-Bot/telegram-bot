#!/bin/bash
cd "$(dirname "$0")/../bot"
source ../venv/bin/activate
echo "==> Starte Telegram Bot ..."
python3 bot.py
status=$?
if [ $status -eq 0 ]; then
  echo "✅ Bot erfolgreich gestartet."
else
  echo "❌ Bot-Start FEHLGESCHLAGEN!"
fi
