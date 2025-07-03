import requests
import logging

class APIClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"GET {url} fehlgeschlagen: {e}")
            raise

    def post(self, endpoint, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"POST {url} fehlgeschlagen: {e}")
            raise

    def patch(self, endpoint, data=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.patch(url, json=data, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"PATCH {url} fehlgeschlagen: {e}")
            raise

# Beispiel für die Initialisierung:
# backend_client = APIClient("https://api.bit-team-bot.online")
# userbot_client = APIClient("http://localhost:9000") 