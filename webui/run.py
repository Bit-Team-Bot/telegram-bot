#!/usr/bin/env python3
"""
Frontend Start-Script für Telegram Bot Management System
"""

import subprocess
import os
import sys

def main():
    print("🌐 Starte Frontend Development Server...")
    
    # Prüfe ob npm installiert ist
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm ist nicht installiert!")
        sys.exit(1)
    
    # Prüfe ob node_modules existiert
    if not os.path.exists("node_modules"):
        print("📦 Installiere Dependencies...")
        subprocess.run(["npm", "install"], check=True)
    
    # Starte Development Server
    print("🚀 Starte Vite Development Server...")
    print("🔗 Frontend wird auf https://webui.bit-team-bot.online verfügbar sein")
    
    try:
        subprocess.run(["npm", "run", "dev"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend Server gestoppt")
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Starten des Frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 