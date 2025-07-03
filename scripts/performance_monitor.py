#!/usr/bin/env python3
"""
Performance-Monitoring-Script für kontinuierliche Überwachung
"""

import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Performance-Monitor für das Telegram Bot System"""
    
    def __init__(self, base_url: str = "https://api.bit-team-bot.online", interval: int = 60):
        self.base_url = base_url
        self.interval = interval
        self.metrics = []
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def check_endpoint(self, endpoint: str, method: str = "GET") -> Dict:
        """Prüft einen einzelnen Endpoint"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url) as response:
                response_time = time.time() - start_time
                return {
                    "endpoint": endpoint,
                    "method": method,
                    "status_code": response.status,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "success": 200 <= response.status < 400
                }
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 0,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    async def check_all_endpoints(self) -> List[Dict]:
        """Prüft alle wichtigen Endpoints"""
        endpoints = [
            "/health",
            "/auth/me",
            "/packages",
            "/users",
            "/admin/users",
            "/monitoring/status"
        ]
        
        tasks = [self.check_endpoint(endpoint) for endpoint in endpoints]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Fehler filtern
        valid_results = []
        for result in results:
            if isinstance(result, dict):
                valid_results.append(result)
            else:
                logger.error(f"Fehler beim Endpoint-Check: {result}")
        
        return valid_results
    
    def calculate_metrics(self, results: List[Dict]) -> Dict:
        """Berechnet Metriken aus den Ergebnissen"""
        if not results:
            return {}
        
        total_requests = len(results)
        successful_requests = sum(1 for r in results if r.get("success", False))
        failed_requests = total_requests - successful_requests
        
        response_times = [r.get("response_time", 0) for r in results if r.get("response_time")]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "endpoints": results
        }
    
    async def monitor_loop(self):
        """Haupt-Monitoring-Schleife"""
        logger.info(f"🚀 Starte Performance-Monitoring für {self.base_url}")
        logger.info(f"⏱️  Intervall: {self.interval} Sekunden")
        
        while True:
            try:
                logger.info("📊 Führe Performance-Check durch...")
                
                results = await self.check_all_endpoints()
                metrics = self.calculate_metrics(results)
                
                # Metriken speichern
                self.metrics.append(metrics)
                
                # Nur die letzten 100 Metriken behalten
                if len(self.metrics) > 100:
                    self.metrics = self.metrics[-100:]
                
                # Status ausgeben
                logger.info(f"✅ Check abgeschlossen:")
                logger.info(f"   - Erfolgsrate: {metrics['success_rate']:.1f}%")
                logger.info(f"   - Durchschnittliche Antwortzeit: {metrics['avg_response_time']:.3f}s")
                logger.info(f"   - Erfolgreiche Requests: {metrics['successful_requests']}/{metrics['total_requests']}")
                
                # Fehler loggen
                failed_endpoints = [r for r in results if not r.get("success", False)]
                if failed_endpoints:
                    logger.warning(f"⚠️  {len(failed_endpoints)} Endpoints fehlgeschlagen:")
                    for endpoint in failed_endpoints:
                        logger.warning(f"   - {endpoint['endpoint']}: {endpoint.get('error', 'HTTP ' + str(endpoint['status_code']))}")
                
                # Metriken in Datei speichern
                self.save_metrics(metrics)
                
            except Exception as e:
                logger.error(f"❌ Fehler im Monitoring-Loop: {e}")
            
            # Warten bis zum nächsten Check
            await asyncio.sleep(self.interval)
    
    def save_metrics(self, metrics: Dict):
        """Speichert Metriken in JSON-Datei"""
        try:
            filename = f"performance_metrics_{datetime.now().strftime('%Y%m%d')}.json"
            
            # Bestehende Metriken laden
            existing_metrics = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        existing_metrics = json.load(f)
                except:
                    existing_metrics = []
            
            # Neue Metriken hinzufügen
            existing_metrics.append(metrics)
            
            # Speichern
            with open(filename, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Metriken: {e}")
    
    def get_summary(self, hours: int = 24) -> Dict:
        """Gibt eine Zusammenfassung der letzten X Stunden"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics 
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "Keine Daten für den angegebenen Zeitraum"}
        
        total_requests = sum(m['total_requests'] for m in recent_metrics)
        total_successful = sum(m['successful_requests'] for m in recent_metrics)
        avg_success_rate = sum(m['success_rate'] for m in recent_metrics) / len(recent_metrics)
        
        all_response_times = []
        for m in recent_metrics:
            for endpoint in m.get('endpoints', []):
                if endpoint.get('response_time'):
                    all_response_times.append(endpoint['response_time'])
        
        avg_response_time = sum(all_response_times) / len(all_response_times) if all_response_times else 0
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "total_successful": total_successful,
            "success_rate": avg_success_rate,
            "avg_response_time": avg_response_time,
            "checks_performed": len(recent_metrics)
        }

async def main():
    """Hauptfunktion"""
    # Konfiguration aus Umgebungsvariablen
    base_url = os.getenv("MONITOR_URL", "https://api.bit-team-bot.online")
    interval = int(os.getenv("MONITOR_INTERVAL", "60"))
    
    async with PerformanceMonitor(base_url, interval) as monitor:
        await monitor.monitor_loop()

if __name__ == "__main__":
    asyncio.run(main()) 