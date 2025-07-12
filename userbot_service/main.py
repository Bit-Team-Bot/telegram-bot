import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Finde das Root-Verzeichnis und lade .env
root_dir = Path(__file__).parent.parent
env_file = root_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from userbot_manager import UserbotManager
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

# CORS-Middleware aktivieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Für Entwicklung, später ggf. einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

userbot_manager = UserbotManager()

class PhoneNumberRequest(BaseModel):
    phone_number: str

class CodeRequest(BaseModel):
    phone_number: str
    code: str
    password: Optional[str] = None
    
    class Config:
        # Erlaube zusätzliche Felder und ignoriere sie
        extra = "ignore"

@app.get("/")
async def root():
    return {"message": "Userbot Service läuft"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/manager/create_session")
async def create_session(data: PhoneNumberRequest):
    return await userbot_manager.create_session(data.phone_number)

@app.post("/manager/send_code")
async def send_code(data: PhoneNumberRequest):
    return await userbot_manager.send_code(data.phone_number)

@app.post("/manager/verify_code")
async def verify_code(data: CodeRequest):
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🚀 VERIFY_CODE ENDPOINT CALLED für {data.phone_number} mit Code {data.code}")
    result = await userbot_manager.verify_code(data.phone_number, data.code, data.password)
    logger.info(f"🚀 VERIFY_CODE RESULT: {result}")
    return result

@app.get("/manager/session_status/{phone_number}")
async def get_session_status(phone_number: str):
    return await userbot_manager.get_session_status(phone_number)

@app.post("/manager/disconnect_session")
async def disconnect_session(data: PhoneNumberRequest):
    return await userbot_manager.disconnect_session(data.phone_number)

@app.get("/manager/chats/{phone_number}")
async def get_chats(phone_number: str):
    return await userbot_manager.get_chats(phone_number)

@app.post("/manager/cleanup_inactive_sessions")
async def cleanup_inactive_sessions():
    return await userbot_manager.cleanup_inactive_sessions()

@app.get("/manager/active_sessions_count")
def get_active_sessions_count():
    return {"active_sessions_count": userbot_manager.get_active_sessions_count()}

@app.get("/manager/all_sessions")
def get_all_sessions():
    return {"sessions": userbot_manager.get_all_sessions()}
