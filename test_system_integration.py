#!/usr/bin/env python3
"""
System-Integrations-Test für Bit-Team-Bot
Testet die wichtigsten Kommunikationswege zwischen Bot, Backend, WebUI und Userbot-Service.
"""

import requests
import json
import sys
from time import sleep
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
WEBUI_URL = os.getenv("WEBUI_URL")
USERBOT_URL = os.getenv("USERBOT_URL")

TEST_USER = {
    "telegram_id": "999999999",
    "user_name": "IntegrationTest",
    "first_name": "Integration",
    "last_name": "Test",
    "username": "integrationtest",
    "phone": "+49999999999"
}

def print_result(name, success, info=None):
    status = "✅" if success else "❌"
    print(f"{status} {name}" + (f" - {info}" if info else ""))

def test_backend_health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print_result("Backend Health", r.status_code == 200)
        return r.status_code == 200
    except Exception as e:
        print_result("Backend Health", False, str(e))
        return False

def test_webui_health():
    try:
        r = requests.get(WEBUI_URL, timeout=5)
        ok = r.status_code == 200 and ("<html" in r.text.lower())
        print_result("WebUI erreichbar", ok)
        return ok
    except Exception as e:
        print_result("WebUI erreichbar", False, str(e))
        return False

def test_userbot_status():
    try:
        r = requests.get(f"{USERBOT_URL}/status", timeout=5)
        ok = r.status_code == 200 and "service" in r.json()
        print_result("Userbot Status", ok)
        return ok
    except Exception as e:
        print_result("Userbot Status", False, str(e))
        return False

def test_register_user():
    try:
        r = requests.post(f"{BACKEND_URL}/users/register_or_update", json=TEST_USER, timeout=5)
        ok = r.status_code in (200, 201)
        print_result("User anlegen (Backend)", ok, f"Status: {r.status_code}")
        return ok
    except Exception as e:
        print_result("User anlegen (Backend)", False, str(e))
        return False

def test_webui_login_form():
    try:
        r = requests.get(f"{WEBUI_URL}/login", timeout=5)
        ok = r.status_code == 200 and ("login" in r.text.lower() or "telefon" in r.text.lower())
        print_result("WebUI Login-Formular lädt", ok)
        return ok
    except Exception as e:
        print_result("WebUI Login-Formular lädt", False, str(e))
        return False

def main():
    print("\n===== System-Integrations-Test =====\n")
    all_ok = True
    if not test_backend_health():
        all_ok = False
    sleep(1)
    if not test_webui_health():
        all_ok = False
    sleep(1)
    if not test_userbot_status():
        all_ok = False
    sleep(1)
    if not test_register_user():
        all_ok = False
    sleep(1)
    if not test_webui_login_form():
        all_ok = False
    print("\n===== Ergebnis =====")
    if all_ok:
        print("\n🎉 Alle Tests erfolgreich! System-Kommunikation OK.")
    else:
        print("\n⚠️  Mindestens ein Test ist fehlgeschlagen. Siehe oben.")

if __name__ == "__main__":
    main() 