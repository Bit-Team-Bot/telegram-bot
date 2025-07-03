#!/bin/bash

# Wechsle ins Verzeichnis, in dem das Skript liegt, dann ins Projekt-Root
cd "$(dirname "$0")/.."

# Symlink von .env im Root nach webui/.env
# Vorher ggf. alte Datei/Symlink entfernen

if [ -L "webui/.env" ] || [ -f "webui/.env" ]; then
  rm webui/.env
fi

ln -s ../.env webui/.env

echo "Symlink für .env im webui-Verzeichnis wurde erstellt." 