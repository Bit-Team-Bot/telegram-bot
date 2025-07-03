#!/usr/bin/env python3
"""
Haupt-Start-Script für Telegram Bot Management System
Startet alle Services: Backend, Frontend, Bot, Userbot
"""

import subprocess
import os
import sys
import time
import signal
import threading
from pathlib import Path

class SystemManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def start_backend(self):
        """Startet das Backend auf Port 8000"""
        print("🔧 Starte Backend...")
        try:
            process = subprocess.Popen(
                ["python", "run.py"],
                cwd="backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['backend'] = process
            print("✅ Backend gestartet auf https://api.bit-team-bot.online")
            return True
        except Exception as e:
            print(f"❌ Backend Fehler: {e}")
            return False
    
    def start_frontend(self):
        """Startet das Frontend auf Port 8080"""
        print("🌐 Starte Frontend...")
        try:
            process = subprocess.Popen(
                ["python", "run.py"],
                cwd="webui",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['frontend'] = process
            print("✅ Frontend gestartet auf https://webui.bit-team-bot.online")
            return True
        except Exception as e:
            print(f"❌ Frontend Fehler: {e}")
            return False
    
    def start_bot(self):
        """Startet den Telegram Bot"""
        print("🤖 Starte Telegram Bot...")
        try:
            process = subprocess.Popen(
                ["python", "bot.py"],
                cwd="bot",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['bot'] = process
            print("✅ Telegram Bot gestartet")
            return True
        except Exception as e:
            print(f"❌ Bot Fehler: {e}")
            return False
    
    def start_userbot(self):
        """Startet den Userbot Service"""
        print("👤 Starte Userbot Service...")
        try:
            process = subprocess.Popen(
                ["python", "userbot_service.py"],
                cwd="userbot_service",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes['userbot'] = process
            print("✅ Userbot Service gestartet")
            return True
        except Exception as e:
            print(f"❌ Userbot Fehler: {e}")
            return False
    
    def check_health(self):
        """Prüft den Health-Status aller Services"""
        import requests
        
        print("\n📊 System Status:")
        
        # Backend Health Check
        try:
            response = requests.get("https://api.bit-team-bot.online/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend: Gesund")
            else:
                print("⚠️ Backend: Fehler")
        except:
            print("❌ Backend: Nicht erreichbar")
        
        # Frontend Health Check
        try:
            response = requests.get("https://webui.bit-team-bot.online", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend: Gesund")
            else:
                print("⚠️ Frontend: Fehler")
        except:
            print("❌ Frontend: Nicht erreichbar")
    
    def stop_all(self):
        """Stoppt alle Services"""
        print("\n🛑 Stoppe alle Services...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} gestoppt")
            except:
                try:
                    process.kill()
                    print(f"🔪 {name} gewaltsam gestoppt")
                except:
                    pass
    
    def signal_handler(self, signum, frame):
        """Signal Handler für graceful shutdown"""
        print(f"\n📡 Signal {signum} empfangen, stoppe System...")
        self.stop_all()
        sys.exit(0)
    
    def run(self):
        """Hauptfunktion zum Starten des Systems"""
        print("🚀 Telegram Bot Management System")
        print("=" * 50)
        
        # Signal Handler registrieren
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Services starten
        services_started = 0
        
        if self.start_backend():
            services_started += 1
            time.sleep(2)  # Warte bis Backend bereit ist
        
        if self.start_frontend():
            services_started += 1
        
        if self.start_bot():
            services_started += 1
        
        if self.start_userbot():
            services_started += 1
        
        print(f"\n🎉 {services_started}/4 Services gestartet")
        
        # Health Check nach 10 Sekunden
        time.sleep(10)
        self.check_health()
        
        print("\n📋 System läuft... Drücke Ctrl+C zum Beenden")
        print("🔗 Backend: https://api.bit-team-bot.online")
        print("🌐 Frontend: https://webui.bit-team-bot.online")
        
        # Hauptschleife
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Beende System...")
            self.stop_all()

if __name__ == "__main__":
    manager = SystemManager()
    manager.run() 