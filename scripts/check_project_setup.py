#!/usr/bin/env python3
"""
Projekt-Setup-Checker für Telegram Bot Management System
Prüft alle wichtigen Komponenten und Konfigurationen
"""

import os
import sys
import subprocess
import socket
import requests
from pathlib import Path
from typing import Dict, List, Tuple

class ProjectSetupChecker:
    """Prüft das gesamte Projekt-Setup"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {}
        self.errors = []
        self.warnings = []
        
    def check_directory_structure(self) -> Dict:
        """Prüft die Verzeichnisstruktur"""
        print("📁 Prüfe Verzeichnisstruktur...")
        
        required_dirs = [
            "backend",
            "backend/app",
            "backend/app/routes",
            "backend/app/auth",
            "bot",
            "bot/handlers",
            "userbot_service",
            "webui",
            "webui/src",
            "webui/src/components",
            "scripts"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        result = {
            "status": "✅" if not missing_dirs else "❌",
            "missing_dirs": missing_dirs,
            "total_required": len(required_dirs),
            "found": len(required_dirs) - len(missing_dirs)
        }
        
        if missing_dirs:
            self.errors.append(f"Fehlende Verzeichnisse: {', '.join(missing_dirs)}")
        
        return result
    
    def check_python_files(self) -> Dict:
        """Prüft wichtige Python-Dateien"""
        print("🐍 Prüfe Python-Dateien...")
        
        required_files = [
            "backend/app/main.py",
            "backend/app/config.py",
            "backend/app/database.py",
            "backend/app/models.py",
            "backend/run.py",
            "bot/bot.py",
            "bot/config.py",
            "userbot_service/userbot_service.py",
            "userbot_service/config.py",
            "start_system.py"
        ]
        
        missing_files = []
        syntax_errors = []
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
            else:
                # Syntax-Check
                try:
                    subprocess.run(
                        [sys.executable, "-m", "py_compile", str(full_path)],
                        capture_output=True,
                        check=True
                    )
                except subprocess.CalledProcessError:
                    syntax_errors.append(file_path)
        
        result = {
            "status": "✅" if not missing_files and not syntax_errors else "❌",
            "missing_files": missing_files,
            "syntax_errors": syntax_errors,
            "total_required": len(required_files),
            "found": len(required_files) - len(missing_files)
        }
        
        if missing_files:
            self.errors.append(f"Fehlende Dateien: {', '.join(missing_files)}")
        if syntax_errors:
            self.errors.append(f"Syntax-Fehler: {', '.join(syntax_errors)}")
        
        return result
    
    def check_dependencies(self) -> Dict:
        """Prüft Python-Abhängigkeiten"""
        print("📦 Prüfe Python-Abhängigkeiten...")
        
        required_packages = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "requests",
            "aiohttp",
            "pyrogram",
            "telethon",
            "python-dotenv"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        result = {
            "status": "✅" if not missing_packages else "❌",
            "missing_packages": missing_packages,
            "total_required": len(required_packages),
            "found": len(required_packages) - len(missing_packages)
        }
        
        if missing_packages:
            self.errors.append(f"Fehlende Pakete: {', '.join(missing_packages)}")
        
        return result
    
    def check_node_dependencies(self) -> Dict:
        """Prüft Node.js-Abhängigkeiten"""
        print("🟢 Prüfe Node.js-Abhängigkeiten...")
        
        webui_path = self.project_root / "webui"
        if not webui_path.exists():
            return {
                "status": "❌",
                "error": "webui Verzeichnis nicht gefunden",
                "missing_packages": [],
                "total_required": 0,
                "found": 0
            }
        
        try:
            # Prüfe ob package.json existiert
            package_json = webui_path / "package.json"
            if not package_json.exists():
                return {
                    "status": "❌",
                    "error": "package.json nicht gefunden",
                    "missing_packages": [],
                    "total_required": 0,
                    "found": 0
                }
            
            # Prüfe ob node_modules existiert
            node_modules = webui_path / "node_modules"
            if not node_modules.exists():
                return {
                    "status": "⚠️",
                    "warning": "node_modules nicht gefunden - führe 'npm install' aus",
                    "missing_packages": [],
                    "total_required": 0,
                    "found": 0
                }
            
            return {
                "status": "✅",
                "missing_packages": [],
                "total_required": 0,
                "found": 0
            }
            
        except Exception as e:
            return {
                "status": "❌",
                "error": str(e),
                "missing_packages": [],
                "total_required": 0,
                "found": 0
            }
    
    def check_environment_files(self) -> Dict:
        """Prüft Umgebungsdateien"""
        print("🔧 Prüfe Umgebungsdateien...")
        
        env_files = [
            ".env",
            "backend/.env",
            "bot/.env",
            "userbot_service/.env"
        ]
        
        missing_files = []
        for env_file in env_files:
            if not (self.project_root / env_file).exists():
                missing_files.append(env_file)
        
        result = {
            "status": "✅" if not missing_files else "⚠️",
            "missing_files": missing_files,
            "total_required": len(env_files),
            "found": len(env_files) - len(missing_files)
        }
        
        if missing_files:
            self.warnings.append(f"Fehlende .env Dateien: {', '.join(missing_files)}")
        
        return result
    
    def check_online_connectivity(self) -> Dict:
        """Prüft Online-Konnektivität"""
        print("🌐 Prüfe Online-Konnektivität...")
        
        test_urls = [
            "https://api.bit-team-bot.online/health",
            "https://webui.bit-team-bot.online",
            "https://api.telegram.org",
            "https://core.telegram.org"
        ]
        
        results = {}
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                results[url] = {
                    "status": "✅",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds()
                }
            except Exception as e:
                results[url] = {
                    "status": "❌",
                    "error": str(e)
                }
        
        successful_checks = sum(1 for r in results.values() if r["status"] == "✅")
        
        return {
            "status": "✅" if successful_checks == len(test_urls) else "⚠️",
            "urls": results,
            "total_checks": len(test_urls),
            "successful": successful_checks
        }
    
    def check_ports(self) -> Dict:
        """Prüft Port-Verfügbarkeit"""
        print("🔌 Prüfe Port-Verfügbarkeit...")
        
        ports_to_check = [8000, 8080, 9000]
        results = {}
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    results[port] = {
                        "status": "❌" if result == 0 else "✅",
                        "available": result != 0
                    }
            except Exception as e:
                results[port] = {
                    "status": "❌",
                    "error": str(e)
                }
        
        available_ports = sum(1 for r in results.values() if r.get("available", False))
        
        return {
            "status": "✅" if available_ports == len(ports_to_check) else "⚠️",
            "ports": results,
            "total_ports": len(ports_to_check),
            "available": available_ports
        }
    
    def run_all_checks(self) -> Dict:
        """Führt alle Checks aus"""
        print("🚀 Starte Projekt-Setup-Check...")
        print("=" * 60)
        
        checks = [
            ("directory_structure", self.check_directory_structure),
            ("python_files", self.check_python_files),
            ("dependencies", self.check_dependencies),
            ("node_dependencies", self.check_node_dependencies),
            ("environment_files", self.check_environment_files),
            ("online_connectivity", self.check_online_connectivity),
            ("ports", self.check_ports)
        ]
        
        for check_name, check_func in checks:
            try:
                self.results[check_name] = check_func()
            except Exception as e:
                self.results[check_name] = {
                    "status": "❌",
                    "error": str(e)
                }
                self.errors.append(f"{check_name}: {e}")
        
        return self.results
    
    def print_summary(self):
        """Gibt eine Zusammenfassung aus"""
        print("\n" + "=" * 60)
        print("PROJEKT-SETUP-CHECK ZUSAMMENFASSUNG")
        print("=" * 60)
        
        total_checks = len(self.results)
        successful_checks = sum(1 for r in self.results.values() if r.get("status") == "✅")
        warning_checks = sum(1 for r in self.results.values() if r.get("status") == "⚠️")
        failed_checks = total_checks - successful_checks - warning_checks
        
        print(f"📊 Gesamt-Checks: {total_checks}")
        print(f"✅ Erfolgreich: {successful_checks}")
        print(f"⚠️  Warnungen: {warning_checks}")
        print(f"❌ Fehler: {failed_checks}")
        
        if self.errors:
            print(f"\n🚨 FEHLER:")
            for error in self.errors:
                print(f"   - {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNUNGEN:")
            for warning in self.warnings:
                print(f"   - {warning}")
        
        if not self.errors and not self.warnings:
            print(f"\n🎉 Alle Checks erfolgreich! Das Projekt ist bereit.")
        elif not self.errors:
            print(f"\n⚠️  Projekt ist funktionsfähig, aber es gibt Warnungen.")
        else:
            print(f"\n❌ Projekt hat Fehler, die behoben werden müssen.")

def main():
    """Hauptfunktion"""
    checker = ProjectSetupChecker()
    results = checker.run_all_checks()
    checker.print_summary()
    
    # Exit-Code basierend auf Ergebnissen
    if checker.errors:
        sys.exit(1)
    elif checker.warnings:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 