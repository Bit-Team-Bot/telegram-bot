#!/usr/bin/env python3
"""
Backend Start-Script für Telegram Bot Management System
"""

import uvicorn
import os
from app.main import app
from app.config import settings

if __name__ == "__main__":
    # Port aus Umgebungsvariable oder Standard 8000
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    print(f"🚀 Starte Backend auf {host}:{port}")
    print(f"📊 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Health Check: https://api.bit-team-bot.online/health")
    
    # Log-Level mit Fallback
    log_level = settings.LOG_LEVEL.lower() if settings.LOG_LEVEL.lower() in ['debug', 'info', 'warning', 'error', 'critical'] else 'info'
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=settings.ENVIRONMENT == "development",
        log_level=log_level
    ) 