import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import Dict, List

class PerformanceTester:
    """Performance-Tester für das Telegram Bot System"""
    
    def __init__(self, base_url: str = "https://api.bit-team-bot.online"):
        self.base_url = base_url
        self.results = []
        
    async def test_endpoint(self, endpoint: str, method: str = "GET", iterations: int = 10) -> Dict:
        """Testet einen Endpoint mit mehreren Iterationen"""
        url = f"{self.base_url}{endpoint}"
        response_times = []
        status_codes = []
        errors = []
        
        print(f"🧪 Teste {method} {endpoint} ({iterations} Iterationen)...")
        
        async with aiohttp.ClientSession() as session:
            for i in range(iterations):
                start_time = time.time()
                try:
                    async with session.request(method, url) as response:
                        response_time = time.time() - start_time
                        response_times.append(response_time)
                        status_codes.append(response.status)
                        
                        if response.status >= 400:
                            errors.append(f"Iteration {i+1}: HTTP {response.status}")
                            
                except Exception as e:
                    response_time = time.time() - start_time
                    response_times.append(response_time)
                    status_codes.append(0)
                    errors.append(f"Iteration {i+1}: {str(e)}")
                
                # Kurze Pause zwischen Requests
                await asyncio.sleep(0.1)
        
        # Statistiken berechnen
        successful_requests = sum(1 for code in status_codes if 200 <= code < 400)
        success_rate = (successful_requests / len(status_codes)) * 100 if status_codes else 0
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "successful_requests": successful_requests,
            "total_requests": len(status_codes),
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "status_codes": status_codes,
            "errors": errors,
            "timestamp": datetime.now().isoformat()
        }
    
    async def run_full_test(self) -> List[Dict]:
        """Führt einen vollständigen Performance-Test durch"""
        print("🚀 Starte vollständigen Performance-Test...")
        print(f"🎯 Ziel-URL: {self.base_url}")
        print("=" * 60)
        
        # Endpoints zum Testen
        endpoints = [
            ("/health", "GET", 20),
            ("/auth/me", "GET", 10),
            ("/packages", "GET", 10),
            ("/users", "GET", 10),
            ("/admin/users", "GET", 5),
            ("/monitoring/status", "GET", 10)
        ]
        
        results = []
        for endpoint, method, iterations in endpoints:
            result = await self.test_endpoint(endpoint, method, iterations)
            results.append(result)
            
            # Zwischenergebnis ausgeben
            print(f"✅ {endpoint}: {result['success_rate']:.1f}% Erfolg, "
                  f"{result['avg_response_time']:.3f}s avg")
        
        self.results = results
        return results
    
    def generate_report(self) -> Dict:
        """Generiert einen Performance-Report"""
        if not self.results:
            return {"error": "Keine Testergebnisse verfügbar"}
        
        # Gesamtstatistiken
        total_requests = sum(r['total_requests'] for r in self.results)
        total_successful = sum(r['successful_requests'] for r in self.results)
        overall_success_rate = (total_successful / total_requests) * 100 if total_requests > 0 else 0
        
        # Response-Zeiten
        all_response_times = []
        for result in self.results:
            all_response_times.extend([
                result['avg_response_time'],
                result['min_response_time'],
                result['max_response_time']
            ])
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        max_response_time = max(all_response_times) if all_response_times else 0
        
        # Fehler sammeln
        all_errors = []
        for result in self.results:
            all_errors.extend(result['errors'])
        
        # Endpoint-spezifische Statistiken
        endpoint_stats = {}
        for result in self.results:
            endpoint_stats[result['endpoint']] = {
                "success_rate": result['success_rate'],
                "avg_response_time": result['avg_response_time'],
                "total_requests": result['total_requests'],
                "errors": len(result['errors'])
            }
        
        report = {
            "test_info": {
                "base_url": self.base_url,
                "timestamp": datetime.now().isoformat(),
                "total_endpoints_tested": len(self.results)
            },
            "overall_stats": {
                "total_requests": total_requests,
                "successful_requests": total_successful,
                "success_rate": overall_success_rate,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "total_errors": len(all_errors)
            },
            "endpoint_stats": endpoint_stats,
            "errors": all_errors,
            "detailed_results": self.results
        }
        
        return report
    
    def save_report(self, report: Dict, filename: str = None):
        """Speichert den Report in eine JSON-Datei"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Report gespeichert: {filename}")
    
    def print_summary(self, report: Dict):
        """Gibt eine Zusammenfassung des Reports aus"""
        print("\n" + "=" * 60)
        print("PERFORMANCE-TEST ZUSAMMENFASSUNG")
        print("=" * 60)
        
        overall = report['overall_stats']
        print(f"🎯 Getestete URL: {report['test_info']['base_url']}")
        print(f"📊 Gesamt-Requests: {overall['total_requests']}")
        print(f"✅ Erfolgreiche Requests: {overall['successful_requests']}")
        print(f"📈 Erfolgsrate: {overall['success_rate']:.1f}%")
        print(f"⚡ Durchschnittliche Antwortzeit: {overall['avg_response_time']:.3f}s")
        print(f"🚀 Maximale Antwortzeit: {overall['max_response_time']:.3f}s")
        print(f"❌ Fehler: {overall['total_errors']}")
        
        print(f"\n📋 Endpoint-Details:")
        for endpoint, stats in report['endpoint_stats'].items():
            print(f"   {endpoint}:")
            print(f"     - Erfolgsrate: {stats['success_rate']:.1f}%")
            print(f"     - Antwortzeit: {stats['avg_response_time']:.3f}s")
            print(f"     - Requests: {stats['total_requests']}")
            print(f"     - Fehler: {stats['errors']}")
        
        if report['errors']:
            print(f"\n🚨 Fehler-Details:")
            for error in report['errors'][:5]:  # Nur die ersten 5 Fehler
                print(f"   - {error}")
            if len(report['errors']) > 5:
                print(f"   ... und {len(report['errors']) - 5} weitere")

async def main():
    """Hauptfunktion"""
    import os
    
    # Konfiguration
    base_url = os.getenv("TEST_URL", "https://api.bit-team-bot.online")
    
    # Tester erstellen und ausführen
    tester = PerformanceTester(base_url)
    results = await tester.run_full_test()
    
    # Report generieren
    report = tester.generate_report()
    
    # Zusammenfassung ausgeben
    tester.print_summary(report)
    
    # Report speichern
    tester.save_report(report)

if __name__ == "__main__":
    asyncio.run(main()) 