#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
echo "==> Starte Userbot-Service ..."
uvicorn userbot_service.main:app --host 0.0.0.0 --port 9000
status=$?
if [ $status -eq 0 ]; then
  echo "✅ Userbot-Service erfolgreich gestartet."
else
  echo "❌ Userbot-Service-Start FEHLGESCHLAGEN!"
fi
