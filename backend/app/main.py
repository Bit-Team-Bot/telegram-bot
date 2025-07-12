from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes import admin, auth, signalgroup, group_warning, group_mute, group_kick
from backend.app.database import engine, Base
from backend.app.config import settings
import logging
import uvicorn
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from backend.app.tasks.session_cleanup import run_daily_maintenance
import requests
from datetime import datetime
import pytz

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# LOG_PATH = os.path.join(BASE_DIR, 'dist', 'app.log')

# Logging einrichten
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        # logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Scheduler für automatische Wartung
scheduler = AsyncIOScheduler()

# Datenbank-Tabellen erstellen
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Datenbank-Tabellen erfolgreich erstellt")
except Exception as e:
    logger.warning(f"⚠️ Fehler beim Erstellen der Datenbank-Tabellen: {e}")

app = FastAPI(
    title="Telegram Bot Backend",
    description="Backend API für Telegram Bot mit Authentifizierung und Paketverwaltung",
    version="1.0.0"
)

# CORS-Konfiguration (nur HTTPS für Sicherheit)
cors_env = os.getenv("CORS_ORIGINS")
if cors_env:
    origins = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    origins = [
        "https://webui.bit-team-bot.online",
        "https://bit-team-bot.online",
        "https://www.bit-team-bot.online",
        "https://api.bit-team-bot.online",
        "https://web.telegram.org",
        "https://t.me"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Routen einbinden
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(signalgroup.router)
app.include_router(group_warning.router)
app.include_router(group_mute.router)
app.include_router(group_kick.router)

# Importiere und binde alle anderen Router ein
try:
    # Versuche zuerst die Router aus backend.app/routes zu importieren
    from backend.app.routes import packages, payments, users, monitoring, wallet, dashboard, admin_packages, user_packages, groups, support, userbot
    
    app.include_router(packages.router, prefix="/packages", tags=["Packages"])
    app.include_router(payments.router, prefix="/payments", tags=["Payments"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
    app.include_router(wallet.router, prefix="/wallet", tags=["Wallet"])
    app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
    app.include_router(admin_packages.router, tags=["Admin Packages"])
    app.include_router(user_packages.router, tags=["User Packages"])
    app.include_router(groups.router, prefix="/groups", tags=["Groups"])
    app.include_router(support.router, prefix="/support", tags=["Support"])
    app.include_router(userbot.router, tags=["Userbot"])
    
    logger.info("✅ Alle Router erfolgreich eingebunden")
except ImportError as e:
    logger.warning(f"⚠️ Einige Router konnten nicht eingebunden werden: {e}")
    # Fallback: Erstelle einfache Mock-Routen
    from fastapi import APIRouter
    
    # Mock Packages Router
    packages_router = APIRouter()
    @packages_router.get("/")
    async def get_packages():
        return [
            {"id": 1, "name": "Basic", "price": 99, "duration_days": 30, "features": ["Basic Signals", "1 Group"], "featured": False},
            {"id": 2, "name": "Pro", "price": 299, "duration_days": 90, "features": ["Premium Signals", "3 Groups"], "featured": True},
            {"id": 3, "name": "Expert", "price": 599, "duration_days": 180, "features": ["Expert Signals", "5 Groups"], "featured": False},
            {"id": 4, "name": "Lifetime", "price": 1999, "duration_days": 36500, "features": ["All Features", "Unlimited"], "featured": False}
        ]
    
    app.include_router(packages_router, prefix="/packages", tags=["Packages"])
    logger.info("✅ Mock Packages Router eingebunden")

@app.get("/")
async def root():
    """Root-Endpoint"""
    return {
        "message": "Telegram Bot Backend API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/auth",
            "admin": "/admin",
            "packages": "/packages",
            "payments": "/payments",
            "users": "/users",
            "monitoring": "/monitoring",
            "wallet": "/wallet"
        }
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/status")
async def status():
    """Einfacher Status-Endpoint"""
    return {
        "status": "online",
        "service": "backend",
        "version": "1.0.0"
    }

@app.get("/test-headers")
async def test_headers(request: Request):
    return dict(request.headers)

@app.get("/system-status")
async def system_status():
    services = {
        "backend": "http://localhost:8000/health",
        "userbot": "http://localhost:9000/health",
        "webui": "http://localhost:8080/health"
    }
    status = {}
    for name, url in services.items():
        try:
            r = requests.get(url, timeout=2)
            status[name] = r.status_code == 200
        except Exception as e:
            status[name] = False
    return status

@app.get("/time")
async def get_time():
    tz = pytz.timezone("Europe/Berlin")
    now = datetime.now(tz)
    return {"datetime": now.isoformat(), "timezone": "Europe/Berlin"}

@app.on_event("startup")
async def startup_event():
    """Startup-Event"""
    logger.info("🚀 Backend wird gestartet...")
    logger.info(f"📍 Server läuft auf {settings.HOST}:{settings.PORT}")
    
    # Starte Scheduler für automatische Wartung
    try:
        scheduler.add_job(
            run_daily_maintenance,
            'cron',
            hour=2,  # Täglich um 2:00 Uhr
            minute=0,
            id='daily_maintenance'
        )
        scheduler.start()
        logger.info("✅ Automatische Wartung geplant (täglich um 2:00 Uhr)")
    except Exception as e:
        logger.error(f"❌ Fehler beim Starten des Schedulers: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown-Event"""
    logger.info("🛑 Backend wird gestoppt...")
    
    # Stoppe Scheduler
    try:
        scheduler.shutdown()
        logger.info("✅ Scheduler gestoppt")
    except Exception as e:
        logger.error(f"❌ Fehler beim Stoppen des Schedulers: {e}")

# Server starten
if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST or "0.0.0.0",
        port=settings.PORT or 8000,
        reload=True,
        log_level=(settings.LOG_LEVEL or "info").lower()
    ) 