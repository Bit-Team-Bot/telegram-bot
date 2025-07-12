import requests

BASE_URL = "http://localhost:8000"
PHONE = "+4917680561392"

def test_health():
    print("Teste /health ...")
    r = requests.get(f"{BASE_URL}/health")
    print("Status:", r.status_code)
    print("Antwort:", r.text)

def test_auth_request_code():
    print("Teste /auth/request-code ...")
    r = requests.post(f"{BASE_URL}/auth/request-code", json={"phone": PHONE})
    print("Status:", r.status_code)
    try:
        print("Antwort:", r.json())
    except Exception:
        print("Antwort (kein JSON):", r.text)

def test_userbot_create_session():
    print("Teste /userbot/create-session ...")
    r = requests.post(f"{BASE_URL}/userbot/create-session", json={"phone_number": PHONE})
    print("Status:", r.status_code)
    try:
        print("Antwort:", r.json())
    except Exception:
        print("Antwort (kein JSON):", r.text)

def test_userbot_session_status():
    print("Teste /userbot/session-status ...")
    r = requests.get(f"{BASE_URL}/userbot/session-status/{PHONE}")
    print("Status:", r.status_code)
    try:
        print("Antwort:", r.json())
    except Exception:
        print("Antwort (kein JSON):", r.text)

def test_userbot_chats():
    print("Teste /userbot/chats ...")
    r = requests.get(f"{BASE_URL}/userbot/chats/{PHONE}")
    print("Status:", r.status_code)
    try:
        print("Antwort:", r.json())
    except Exception:
        print("Antwort (kein JSON):", r.text)

if __name__ == "__main__":
    test_health()
    print("-" * 40)
    test_auth_request_code()
    print("-" * 40)
    test_userbot_create_session()
    print("-" * 40)
    test_userbot_session_status()
    print("-" * 40)
    test_userbot_chats()