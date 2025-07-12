"""
Erweitertes Error-Handling und Logging-System
Stellt sicher, dass alle Fehler korrekt protokolliert und behandelt werden
"""
import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

# Logger-Konfiguration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend_debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedErrorHandler:
    """Erweiterter Error-Handler mit detailliertem Logging"""
    
    def __init__(self):
        self.error_log = []
        self.max_log_entries = 1000
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None, user_id: Optional[int] = None):
        """Loggt einen Fehler mit Kontext-Informationen"""
        try:
            error_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {},
                "user_id": user_id
            }
            
            # Fehler in Log-Datei schreiben
            logger.error(f"ERROR: {json.dumps(error_info, indent=2)}")
            
            # Fehler in Memory-Log speichern
            self.error_log.append(error_info)
            
            # Alte Einträge entfernen
            if len(self.error_log) > self.max_log_entries:
                self.error_log = self.error_log[-self.max_log_entries:]
            
            # Kritische Fehler an Monitoring-Service senden
            if self._is_critical_error(error):
                self._send_error_to_monitoring(error_info)
                
        except Exception as e:
            logger.error(f"Fehler beim Logging: {e}")
    
    def handle_database_error(self, error: SQLAlchemyError, operation: str, context: Optional[Dict] = None) -> Dict:
        """Behandelt Datenbankfehler speziell"""
        error_context = {
            "operation": operation,
            "database_error_type": type(error).__name__,
            "context": context or {}
        }
        
        self.log_error(error, error_context)
        
        # Spezifische Behandlung je nach Fehlertyp
        if "duplicate key" in str(error).lower():
            return {
                "success": False,
                "error": "Datensatz bereits vorhanden",
                "error_code": "DUPLICATE_ENTRY",
                "details": "Ein Datensatz mit diesen Daten existiert bereits"
            }
        elif "foreign key" in str(error).lower():
            return {
                "success": False,
                "error": "Referenzfehler",
                "error_code": "FOREIGN_KEY_VIOLATION",
                "details": "Referenzierte Daten existieren nicht"
            }
        elif "connection" in str(error).lower():
            return {
                "success": False,
                "error": "Datenbankverbindung fehlgeschlagen",
                "error_code": "DB_CONNECTION_ERROR",
                "details": "Verbindung zur Datenbank konnte nicht hergestellt werden"
            }
        else:
            return {
                "success": False,
                "error": "Datenbankfehler",
                "error_code": "DATABASE_ERROR",
                "details": str(error)
            }
    
    def handle_api_error(self, error: Exception, endpoint: str, request_data: Optional[Dict] = None) -> Dict:
        """Behandelt API-Fehler"""
        error_context = {
            "endpoint": endpoint,
            "request_data": request_data or {},
            "error_type": "API_ERROR"
        }
        
        self.log_error(error, error_context)
        
        return {
            "success": False,
            "error": "API-Fehler",
            "error_code": "API_ERROR",
            "details": str(error),
            "endpoint": endpoint
        }
    
    def handle_userbot_error(self, error: Exception, session_id: int, operation: str) -> Dict:
        """Behandelt Userbot-spezifische Fehler"""
        error_context = {
            "session_id": session_id,
            "operation": operation,
            "error_type": "USERBOT_ERROR"
        }
        
        self.log_error(error, error_context)
        
        return {
            "success": False,
            "error": "Userbot-Fehler",
            "error_code": "USERBOT_ERROR",
            "details": str(error),
            "session_id": session_id,
            "operation": operation
        }
    
    def handle_payment_error(self, error: Exception, payment_id: int, user_id: int) -> Dict:
        """Behandelt Payment-spezifische Fehler"""
        error_context = {
            "payment_id": payment_id,
            "user_id": user_id,
            "error_type": "PAYMENT_ERROR"
        }
        
        self.log_error(error, error_context)
        
        return {
            "success": False,
            "error": "Zahlungsfehler",
            "error_code": "PAYMENT_ERROR",
            "details": str(error),
            "payment_id": payment_id
        }
    
    def create_error_response(self, error: Exception, status_code: int = 500) -> JSONResponse:
        """Erstellt eine strukturierte Fehlerantwort"""
        error_info = {
            "success": False,
            "error": {
                "type": type(error).__name__,
                "message": str(error),
                "timestamp": datetime.utcnow().isoformat(),
                "error_code": self._get_error_code(error)
            }
        }
        
        # Fehler loggen
        self.log_error(error, {"status_code": status_code})
        
        return JSONResponse(
            status_code=status_code,
            content=error_info
        )
    
    def _is_critical_error(self, error: Exception) -> bool:
        """Bestimmt ob ein Fehler kritisch ist"""
        critical_error_types = [
            "DatabaseConnectionError",
            "PaymentProcessingError",
            "UserbotSessionError",
            "SecurityViolationError"
        ]
        
        return any(error_type in str(error) for error_type in critical_error_types)
    
    def _get_error_code(self, error: Exception) -> str:
        """Ermittelt einen Error-Code basierend auf dem Fehlertyp"""
        if isinstance(error, HTTPException):
            return f"HTTP_{error.status_code}"
        elif isinstance(error, SQLAlchemyError):
            return "DATABASE_ERROR"
        elif "payment" in str(error).lower():
            return "PAYMENT_ERROR"
        elif "userbot" in str(error).lower():
            return "USERBOT_ERROR"
        elif "authentication" in str(error).lower():
            return "AUTH_ERROR"
        else:
            return "GENERAL_ERROR"
    
    def _send_error_to_monitoring(self, error_info: Dict):
        """Sendet kritische Fehler an den Monitoring-Service"""
        try:
            # Hier würde die Integration mit einem Monitoring-Service erfolgen
            # z.B. Sentry, LogRocket, etc.
            logger.critical(f"KRITISCHER FEHLER: {json.dumps(error_info)}")
            
        except Exception as e:
            logger.error(f"Fehler beim Senden an Monitoring: {e}")
    
    def get_error_log(self, limit: int = 100) -> List[Dict]:
        """Gibt die letzten Fehler-Logs zurück"""
        return self.error_log[-limit:]
    
    def clear_error_log(self):
        """Löscht den Error-Log"""
        self.error_log.clear()

# Globale Instanz
error_handler = EnhancedErrorHandler()

# FastAPI Exception Handler
async def global_exception_handler(request: Request, exc: Exception):
    """Globaler Exception-Handler für FastAPI"""
    return error_handler.create_error_response(exc)

# Middleware für Request-Logging
async def request_logging_middleware(request: Request, call_next):
    """Middleware für Request-Logging"""
    start_time = datetime.utcnow()
    
    # Request-Logging
    logger.info(f"REQUEST: {request.method} {request.url} - {request.client.host}")
    
    try:
        response = await call_next(request)
        
        # Response-Logging
        process_time = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"RESPONSE: {response.status_code} - {process_time:.3f}s")
        
        return response
        
    except Exception as e:
        # Error-Logging
        error_handler.log_error(e, {
            "request_method": request.method,
            "request_url": str(request.url),
            "client_host": request.client.host
        })
        raise 