#!/bin/bash
cd "$(dirname "$0")/.."
source venv/bin/activate
echo "==> Starte Backend (FastAPI) ..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 \
  --reload
status=$?
if [ $status -eq 0 ]; then
  echo "✅ Backend erfolgreich gestartet."
else
  echo "❌ Backend-Start FEHLGESCHLAGEN!"
fi
