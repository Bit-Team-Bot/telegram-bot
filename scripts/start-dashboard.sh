#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate

echo "==> Starte WebUI Frontend ..."
cd webui

# Vue CLI ggf. ausführbar machen
chmod +x node_modules/.bin/vue-cli-service 2>/dev/null

npx vite --host 0.0.0.0 --port 8080
status=$?
if [ $status -eq 0 ]; then
  echo "✅ WebUI erfolgreich gestartet."
else
  echo "❌ WebUI-Start FEHLGESCHLAGEN!"
fi
