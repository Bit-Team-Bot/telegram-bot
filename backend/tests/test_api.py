from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Beispiel-Testdaten (ggf. anpassen)
TEST_PHONE = "+49123456789"
TEST_TELEGRAM_ID = "test_telegram_id_123"


def test_register_and_login():
    # Registrierung/Login-Code anfordern
    resp = client.post("/auth/request-code", json={"phone": TEST_PHONE, "telegram_id": TEST_TELEGRAM_ID})
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data or "detail" in data


def test_get_packages():
    resp = client.get("/packages")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_dashboard_stats_unauth():
    resp = client.get("/dashboard/stats")
    assert resp.status_code in (401, 403)  # Ohne Auth sollte abgelehnt werden

# Weitere Tests können mit Auth-Token ergänzt werden, z.B.:
# - Paket kaufen
# - Userbot-Session anlegen
# - Payment anlegen
# - User löschen
# ...

# Für vollständige Tests: Token-Handling und Setup/Teardown für Testdaten ergänzen! 