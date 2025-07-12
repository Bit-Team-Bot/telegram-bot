from typing import Dict, Any, List, Optional
from collections import defaultdict, deque
import sqlite3
import logging

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance-Metrik für API-Calls"""
    endpoint: str
    method: str
    response_time: float
    status_code: int
    timestamp: datetime
    user_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class SystemMetric:
    """System-Metrik für Ressourcen"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    timestamp: datetime

class MonitoringSystem:
    """Erweitertes Monitoring-System für das Backend"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.performance_metrics = deque(maxlen=max_history)
        self.system_metrics = deque(maxlen=max_history)
        self.error_counts = defaultdict(int)
        self.endpoint_stats = defaultdict(lambda: {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'avg_response_time': 0.0,
            'min_response_time': float('inf'),
            'max_response_time': 0.0
        })
        
        # Monitoring-Datenbank initialisieren
        self.init_monitoring_db()
    
    def init_monitoring_db(self):
        """Initialisiert die Monitoring-Datenbank"""
        try:
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            
            # Performance-Metriken Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    status_code INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    error_message TEXT
                )
            ''')
            
            # System-Metriken Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    disk_percent REAL NOT NULL,
                    active_connections INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Error-Logs Tabelle
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type TEXT NOT NULL,
                    error_message TEXT NOT NULL,
                    endpoint TEXT,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    stack_trace TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Monitoring-Datenbank initialisiert")
            
        except Exception as e:
            logger.error(f"Fehler beim Initialisieren der Monitoring-Datenbank: {e}")
    
    def record_performance(self, metric: PerformanceMetric):
        """Zeichnet Performance-Metriken auf"""
        try:
            # In Memory speichern
            self.performance_metrics.append(metric)
            
            # Endpoint-Statistiken aktualisieren
            endpoint_key = f"{metric.method} {metric.endpoint}"
            stats = self.endpoint_stats[endpoint_key]
            stats['total_calls'] += 1
            
            if 200 <= metric.status_code < 400:
                stats['successful_calls'] += 1
            else:
                stats['failed_calls'] += 1
                self.error_counts[metric.status_code] += 1
            
            # Response-Zeit-Statistiken aktualisieren
            if stats['total_calls'] == 1:
                stats['avg_response_time'] = metric.response_time
                stats['min_response_time'] = metric.response_time
                stats['max_response_time'] = metric.response_time
            else:
                # Gleitender Durchschnitt
                stats['avg_response_time'] = (
                    (stats['avg_response_time'] * (stats['total_calls'] - 1) + metric.response_time) 
                    / stats['total_calls']
                )
                stats['min_response_time'] = min(stats['min_response_time'], metric.response_time)
                stats['max_response_time'] = max(stats['max_response_time'], metric.response_time)
            
            # In Datenbank speichern
            self.save_performance_to_db(metric)
            
        except Exception as e:
            logger.error(f"Fehler beim Aufzeichnen der Performance-Metrik: {e}")
    
    def record_system_metric(self, metric: SystemMetric):
        """Zeichnet System-Metriken auf"""
        try:
            self.system_metrics.append(metric)
            self.save_system_to_db(metric)
        except Exception as e:
            logger.error(f"Fehler beim Aufzeichnen der System-Metrik: {e}")
    
    def record_error(self, error_type: str, error_message: str, endpoint: Optional[str] = None, 
                    user_id: Optional[str] = None, stack_trace: Optional[str] = None):
        """Zeichnet Fehler auf"""
        try:
            error_metric = {
                'error_type': error_type,
                'error_message': error_message,
                'endpoint': endpoint,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'stack_trace': stack_trace
            }
            
            # In Datenbank speichern
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO error_logs (error_type, error_message, endpoint, user_id, timestamp, stack_trace)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (error_type, error_message, endpoint, user_id, 
                  error_metric['timestamp'], stack_trace))
            conn.commit()
            conn.close()
            
            logger.error(f"Fehler aufgezeichnet: {error_type} - {error_message}")
            
        except Exception as e:
            logger.error(f"Fehler beim Aufzeichnen des Fehlers: {e}")
    
    def save_performance_to_db(self, metric: PerformanceMetric):
        """Speichert Performance-Metrik in Datenbank"""
        try:
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO performance_metrics 
                (endpoint, method, response_time, status_code, timestamp, user_id, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (metric.endpoint, metric.method, metric.response_time, metric.status_code,
                  metric.timestamp.isoformat(), metric.user_id, metric.error_message))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Performance-Metrik: {e}")
    
    def save_system_to_db(self, metric: SystemMetric):
        """Speichert System-Metrik in Datenbank"""
        try:
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, disk_percent, active_connections, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (metric.cpu_percent, metric.memory_percent, metric.disk_percent,
                  metric.active_connections, metric.timestamp.isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Fehler beim Speichern der System-Metrik: {e}")
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Gibt Performance-Zusammenfassung zurück"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Aus Datenbank laden
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT endpoint, method, response_time, status_code, timestamp
                FROM performance_metrics
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            recent_metrics = cursor.fetchall()
            conn.close()
            
            if not recent_metrics:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'success_rate': 0,
                    'top_endpoints': [],
                    'error_distribution': {}
                }
            
            # Statistiken berechnen
            total_requests = len(recent_metrics)
            successful_requests = sum(1 for m in recent_metrics if 200 <= m[3] < 400)
            avg_response_time = sum(m[2] for m in recent_metrics) / total_requests
            
            # Top-Endpoints
            endpoint_counts = defaultdict(int)
            for metric in recent_metrics:
                endpoint_counts[f"{metric[1]} {metric[0]}"] += 1
            
            top_endpoints = sorted(endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Error-Verteilung
            error_distribution = defaultdict(int)
            for metric in recent_metrics:
                if metric[3] >= 400:
                    error_distribution[metric[3]] += 1
            
            return {
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 3),
                'success_rate': round(successful_requests / total_requests * 100, 2),
                'top_endpoints': top_endpoints,
                'error_distribution': dict(error_distribution)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Performance-Zusammenfassung: {e}")
            return {}
    
    def get_system_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Gibt System-Zusammenfassung zurück"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cpu_percent, memory_percent, disk_percent, active_connections, timestamp
                FROM system_metrics
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            ''', (cutoff_time.isoformat(),))
            
            recent_metrics = cursor.fetchall()
            conn.close()
            
            if not recent_metrics:
                return {
                    'current_cpu': 0,
                    'current_memory': 0,
                    'current_disk': 0,
                    'avg_cpu': 0,
                    'avg_memory': 0,
                    'avg_disk': 0
                }
            
            # Aktuelle Werte (neueste Metrik)
            current = recent_metrics[0]
            
            # Durchschnittswerte
            avg_cpu = sum(m[0] for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m[1] for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m[2] for m in recent_metrics) / len(recent_metrics)
            
            return {
                'current_cpu': round(current[0], 1),
                'current_memory': round(current[1], 1),
                'current_disk': round(current[2], 1),
                'avg_cpu': round(avg_cpu, 1),
                'avg_memory': round(avg_memory, 1),
                'avg_disk': round(avg_disk, 1),
                'active_connections': current[3]
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der System-Zusammenfassung: {e}")
            return {}
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Gibt die neuesten Fehler zurück"""
        try:
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT error_type, error_message, endpoint, user_id, timestamp
                FROM error_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            errors = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'error_type': error[0],
                    'error_message': error[1],
                    'endpoint': error[2],
                    'user_id': error[3],
                    'timestamp': error[4]
                }
                for error in errors
            ]
            
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Fehler: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 30):
        """Bereinigt alte Monitoring-Daten"""
        try:
            cutoff_time = datetime.now() - timedelta(days=days)
            
            conn = sqlite3.connect('monitoring.db')
            cursor = conn.cursor()
            
            # Alte Performance-Metriken löschen
            cursor.execute('DELETE FROM performance_metrics WHERE timestamp < ?', 
                          (cutoff_time.isoformat(),))
            
            # Alte System-Metriken löschen
            cursor.execute('DELETE FROM system_metrics WHERE timestamp < ?', 
                          (cutoff_time.isoformat(),))
            
            # Alte Fehler-Logs löschen
            cursor.execute('DELETE FROM error_logs WHERE timestamp < ?', 
                          (cutoff_time.isoformat(),))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Monitoring-Daten älter als {days} Tage wurden bereinigt")
            
        except Exception as e:
            logger.error(f"Fehler beim Bereinigen der Monitoring-Daten: {e}")

# Globale Monitoring-Instanz
monitoring = MonitoringSystem()
