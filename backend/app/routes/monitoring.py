from fastapi import APIRouter, HTTPException
from ..monitoring import monitoring
import psutil
from datetime import datetime
from typing import Dict, Any

router = APIRouter()

@router.get("/performance")
async def get_performance_summary(hours: int = 24) -> Dict[str, Any]:
    """Gibt Performance-Zusammenfassung zurück"""
    try:
        return monitoring.get_performance_summary(hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Performance-Daten: {e}")

@router.get("/system")
async def get_system_summary(hours: int = 24) -> Dict[str, Any]:
    """Gibt System-Zusammenfassung zurück"""
    try:
        system_data = monitoring.get_system_summary(hours)
        
        # Aktuelle System-Metriken hinzufügen
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            system_data.update({
                'current_cpu': round(cpu_percent, 1),
                'current_memory': round(memory.percent, 1),
                'current_disk': round(disk.percent, 1),
                'memory_available_mb': round(memory.available / 1024 / 1024, 1),
                'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 1)
            })
        except ImportError:
            pass  # psutil nicht verfügbar
        
        return system_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der System-Daten: {e}")

@router.get("/errors")
async def get_recent_errors(limit: int = 10) -> Dict[str, Any]:
    """Gibt die neuesten Fehler zurück"""
    try:
        errors = monitoring.get_recent_errors(limit)
        return {
            'errors': errors,
            'total_errors': len(errors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Fehler-Daten: {e}")

@router.get("/endpoints")
async def get_endpoint_stats() -> Dict[str, Any]:
    """Gibt Endpoint-Statistiken zurück"""
    try:
        endpoint_stats = dict(monitoring.endpoint_stats)
        
        # Statistiken für bessere Lesbarkeit formatieren
        formatted_stats = {}
        for endpoint, stats in endpoint_stats.items():
            formatted_stats[endpoint] = {
                'total_calls': stats['total_calls'],
                'successful_calls': stats['successful_calls'],
                'failed_calls': stats['failed_calls'],
                'success_rate': round(stats['successful_calls'] / stats['total_calls'] * 100, 2) if stats['total_calls'] > 0 else 0,
                'avg_response_time': round(stats['avg_response_time'], 3),
                'min_response_time': round(stats['min_response_time'], 3) if stats['min_response_time'] != float('inf') else 0,
                'max_response_time': round(stats['max_response_time'], 3)
            }
        
        return {
            'endpoints': formatted_stats,
            'total_endpoints': len(formatted_stats)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Endpoint-Statistiken: {e}")

@router.post("/cleanup")
async def cleanup_old_data(days: int = 30) -> Dict[str, Any]:
    """Bereinigt alte Monitoring-Daten"""
    try:
        monitoring.cleanup_old_data(days)
        return {
            'message': f'Monitoring-Daten älter als {days} Tage wurden bereinigt',
            'cleanup_date': datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Bereinigen der Daten: {e}")

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """Detaillierter Health-Check mit Monitoring-Daten"""
    try:
        # Performance-Daten der letzten Stunde
        performance = monitoring.get_performance_summary(1)
        
        # System-Daten
        system = monitoring.get_system_summary(1)
        
        # Aktuelle System-Metriken
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            current_system = {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'disk_percent': round(disk.percent, 1),
                'memory_available_mb': round(memory.available / 1024 / 1024, 1),
                'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 1)
            }
        except ImportError:
            current_system = {
                'cpu_percent': 0,
                'memory_percent': 0,
                'disk_percent': 0,
                'memory_available_mb': 0,
                'disk_free_gb': 0
            }
        
        # Gesamtstatus bestimmen
        status = "healthy"
        if performance.get('success_rate', 100) < 95:
            status = "degraded"
        if current_system['cpu_percent'] > 90 or current_system['memory_percent'] > 90:
            status = "warning"
        
        return {
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'performance': performance,
            'system': system,
            'current_system': current_system,
            'monitoring_active': True
        }
    except Exception as e:
        return {
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': str(e),
            'monitoring_active': False
        } 