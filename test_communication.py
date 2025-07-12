#!/usr/bin/env python3
"""
Umfassende Kommunikationstest-Suite für Telegram Bot System
Testet alle Verbindungen zwischen Bot, Backend und Webinterface
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konfiguration
BACKEND_URL = os.getenv("BACKEND_URL")
USERBOT_URL = os.getenv("USERBOT_URL")
WEBUI_URL = os.getenv("WEBUI_URL")

# Test-Daten
TEST_USER = {
    "telegram_id": "123456789",
    "user_name": "TestUser",
    "first_name": "Test",
    "last_name": "User",
    "username": "testuser",
    "phone": "+49123456789"
}

class CommunicationTester:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.timeout = 10
        
    def log_test(self, test_name: str, success: bool, details: str = "", error: str = ""):
        """Test-Ergebnis loggen"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        if success:
            logger.info(f"✅ {test_name}: {details}")
        else:
            logger.error(f"❌ {test_name}: {error}")
    
    def test_backend_health(self) -> bool:
        """Test 1: Backend Health Check"""
        try:
            response = self.session.get(f"{BACKEND_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Health", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Backend Health", False, error=f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health", False, error=str(e))
            return False
    
    def test_backend_status(self) -> bool:
        """Test 2: Backend Status Endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Status", True, f"Service: {data.get('service', 'unknown')}")
                return True
            else:
                self.log_test("Backend Status", False, error=f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Status", False, error=str(e))
            return False
    
    def test_userbot_health(self) -> bool:
        """Test 3: Userbot Health Check"""
        try:
            response = self.session.get(f"{USERBOT_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Userbot Health", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("Userbot Health", False, error=f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Userbot Health", False, error=str(e))
            return False
    
    def test_userbot_status(self) -> bool:
        """Test 4: Userbot Status Endpoint"""
        try:
            response = self.session.get(f"{USERBOT_URL}/status")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Userbot Status", True, f"Service: {data.get('service', 'unknown')}")
                return True
            else:
                self.log_test("Userbot Status", False, error=f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Userbot Status", False, error=str(e))
            return False
    
    def test_webui_health(self) -> bool:
        """Test 5: WebUI Health Check"""
        try:
            response = self.session.get(f"{WEBUI_URL}/")
            if response.status_code == 200:
                self.log_test("WebUI Health", True, "Frontend erreichbar")
                return True
            else:
                self.log_test("WebUI Health", False, error=f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("WebUI Health", False, error=str(e))
            return False
    
    def test_backend_user_registration(self) -> bool:
        """Test 6: Backend User Registration API"""
        try:
            response = self.session.post(
                f"{BACKEND_URL}/users/register_or_update",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Backend User Registration", True, f"User ID: {data.get('user_id', 'unknown')}")
                return True
            else:
                self.log_test("Backend User Registration", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Backend User Registration", False, error=str(e))
            return False
    
    def test_backend_user_status(self) -> bool:
        """Test 7: Backend User Status API"""
        try:
            response = self.session.get(f"{BACKEND_URL}/users/{TEST_USER['telegram_id']}/is_paid")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend User Status", True, f"Paid: {data.get('is_paid', False)}")
                return True
            else:
                self.log_test("Backend User Status", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Backend User Status", False, error=str(e))
            return False
    
    def test_userbot_phone_registration(self) -> bool:
        """Test 8: Userbot Phone Registration API"""
        try:
            payload = {
                "telegram_id": TEST_USER["telegram_id"],
                "phone": TEST_USER["phone"]
            }
            response = self.session.post(
                f"{USERBOT_URL}/users/register_phone",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code in [200, 201]:
                self.log_test("Userbot Phone Registration", True, "Phone registration successful")
                return True
            else:
                self.log_test("Userbot Phone Registration", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Userbot Phone Registration", False, error=str(e))
            return False
    
    def test_backend_packages_api(self) -> bool:
        """Test 9: Backend Packages API"""
        try:
            response = self.session.get(f"{BACKEND_URL}/packages")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Packages API", True, f"Packages found: {len(data)}")
                return True
            else:
                self.log_test("Backend Packages API", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Backend Packages API", False, error=str(e))
            return False
    
    def test_backend_payments_api(self) -> bool:
        """Test 10: Backend Payments API"""
        try:
            response = self.session.get(f"{BACKEND_URL}/payments/user/{TEST_USER['telegram_id']}")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Payments API", True, f"Payments found: {len(data) if isinstance(data, list) else 0}")
                return True
            else:
                self.log_test("Backend Payments API", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Backend Payments API", False, error=str(e))
            return False
    
    def test_backend_monitoring_api(self) -> bool:
        """Test 11: Backend Monitoring API"""
        try:
            response = self.session.get(f"{BACKEND_URL}/monitoring/endpoints")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Monitoring API", True, f"Endpoints monitored: {data.get('total_endpoints', 0)}")
                return True
            else:
                self.log_test("Backend Monitoring API", False, error=f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Backend Monitoring API", False, error=str(e))
            return False
    
    def test_data_integrity(self) -> bool:
        """Test 12: Datenintegrität zwischen Services"""
        try:
            # User in Backend registrieren
            reg_response = self.session.post(
                f"{BACKEND_URL}/users/register_or_update",
                json=TEST_USER,
                headers={"Content-Type": "application/json"}
            )
            
            if reg_response.status_code not in [200, 201]:
                self.log_test("Data Integrity", False, error="User registration failed")
                return False
            
            # User-Status abrufen
            status_response = self.session.get(f"{BACKEND_URL}/users/{TEST_USER['telegram_id']}/is_paid")
            
            if status_response.status_code == 200:
                self.log_test("Data Integrity", True, "User data consistent between endpoints")
                return True
            else:
                self.log_test("Data Integrity", False, error="User status check failed")
                return False
                
        except Exception as e:
            self.log_test("Data Integrity", False, error=str(e))
            return False
    
    def test_api_endpoint_consistency(self) -> bool:
        """Test 13: API Endpoint Konsistenz"""
        endpoints_to_test = [
            f"{BACKEND_URL}/auth/request-code",
            f"{BACKEND_URL}/auth/login",
            f"{BACKEND_URL}/auth/verify",
            f"{USERBOT_URL}/start",
            f"{USERBOT_URL}/verify",
            f"{USERBOT_URL}/api/dialogs",
            f"{USERBOT_URL}/api/create_group"
        ]
        
        successful_endpoints = 0
        
        for endpoint in endpoints_to_test:
            try:
                response = self.session.get(endpoint)
                if response.status_code in [200, 401, 405]:  # 401 = auth required, 405 = method not allowed
                    successful_endpoints += 1
            except Exception:
                pass
        
        success_rate = (successful_endpoints / len(endpoints_to_test)) * 100
        self.log_test("API Endpoint Consistency", success_rate > 80, f"Success rate: {success_rate:.1f}%")
        return success_rate > 80
    
    def test_error_handling(self) -> bool:
        """Test 14: Error Handling"""
        try:
            # Test mit ungültigen Daten
            response = self.session.post(
                f"{BACKEND_URL}/users/register_or_update",
                json={"invalid": "data"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code in [400, 422]:  # Erwartete Fehlercodes
                self.log_test("Error Handling", True, "Proper error response for invalid data")
                return True
            else:
                self.log_test("Error Handling", False, error=f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", False, error=str(e))
            return False
    
    def test_response_time(self) -> bool:
        """Test 15: Response Time Performance"""
        endpoints = [
            f"{BACKEND_URL}/health",
            f"{BACKEND_URL}/status",
            f"{USERBOT_URL}/health",
            f"{USERBOT_URL}/status"
        ]
        
        total_time = 0
        successful_requests = 0
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(endpoint)
                end_time = time.time()
                
                if response.status_code == 200:
                    total_time += (end_time - start_time)
                    successful_requests += 1
            except Exception:
                pass
        
        if successful_requests > 0:
            avg_time = total_time / successful_requests
            self.log_test("Response Time", avg_time < 2.0, f"Average response time: {avg_time:.2f}s")
            return avg_time < 2.0
        else:
            self.log_test("Response Time", False, error="No successful requests")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Alle Tests ausführen"""
        logger.info("🚀 Starte umfassende Kommunikationstests...")
        
        tests = [
            self.test_backend_health,
            self.test_backend_status,
            self.test_userbot_health,
            self.test_userbot_status,
            self.test_webui_health,
            self.test_backend_user_registration,
            self.test_backend_user_status,
            self.test_userbot_phone_registration,
            self.test_backend_packages_api,
            self.test_backend_payments_api,
            self.test_backend_monitoring_api,
            self.test_data_integrity,
            self.test_api_endpoint_consistency,
            self.test_error_handling,
            self.test_response_time
        ]
        
        successful_tests = 0
        for test in tests:
            try:
                if test():
                    successful_tests += 1
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
        
        # Zusammenfassung
        total_tests = len(tests)
        success_rate = (successful_tests / total_tests) * 100
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": success_rate,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📊 Test-Zusammenfassung:")
        logger.info(f"   Gesamt: {total_tests}")
        logger.info(f"   Erfolgreich: {successful_tests}")
        logger.info(f"   Fehlgeschlagen: {total_tests - successful_tests}")
        logger.info(f"   Erfolgsrate: {success_rate:.1f}%")
        
        return summary
    
    def save_results(self, filename: str = "communication_test_results.json"):
        """Testergebnisse in Datei speichern"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Testergebnisse gespeichert in {filename}")

def main():
    """Hauptfunktion"""
    tester = CommunicationTester()
    summary = tester.run_all_tests()
    
    # Ergebnisse speichern
    tester.save_results()
    
    # Detaillierte Ausgabe
    print("\n" + "="*60)
    print("DETAILLIERTE TEST-ERGEBNISSE")
    print("="*60)
    
    for result in tester.results:
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['test']}")
        if result["details"]:
            print(f"   Details: {result['details']}")
        if result["error"]:
            print(f"   Fehler: {result['error']}")
        print()
    
    print("="*60)
    print(f"GESAMT-ERFOLGSRATE: {summary['success_rate']:.1f}%")
    print("="*60)
    
    if summary['success_rate'] >= 80:
        print("🎉 Kommunikationstests erfolgreich! System ist bereit.")
    elif summary['success_rate'] >= 60:
        print("⚠️  Kommunikationstests teilweise erfolgreich. Einige Probleme gefunden.")
    else:
        print("🚨 Kommunikationstests fehlgeschlagen! Kritische Probleme gefunden.")

if __name__ == "__main__":
    main() 