from fastapi import FastAPI, HTTPException, Request
from userbot_handler import UserbotHandler  # Kein Subfolder, Datei liegt im gleichen Ordner wie main.py
from config import API_ID, API_HASH, SESSION_NAME
from pydantic import BaseModel
import asyncio
from userbot_manager import UserbotManager

app = FastAPI()
userbot = UserbotHandler()
userbot_manager = UserbotManager()

class PhoneRequest(BaseModel):
    phone: str

class CodeVerify(BaseModel):
    phone: str
    code: str

class PhoneNumberRequest(BaseModel):
    phone_number: str

class CodeRequest(BaseModel):
    phone_number: str
    code: str
    password: str = None

@app.on_event("startup")
async def startup_event():
    await userbot.start()

@app.post("/start")
async def start_userbot(data: PhoneRequest):
    try:
        result = await userbot.send_verification_code(data.phone)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify")
async def verify_code(data: CodeVerify):
    result = userbot.verify_code(data.phone, data.code)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/api/dialogs")
async def get_dialogs():
    try:
        dialogs = await userbot.get_dialogs()
        return dialogs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/create_group")
async def create_group(title: str, supergroup: bool = False):
    try:
        result = await userbot.create_group(title, supergroup)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/send_message")
async def send_message(group_id: int, message: str):
    try:
        result = await userbot.send_message(group_id, message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add_user_to_group")
async def add_user_to_group(user_id: int, group_id: int):
    try:
        result = await userbot.add_user_to_group(user_id, group_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transfer_ownership")
async def transfer_ownership(group_id: int, new_owner_id: int):
    try:
        result = await userbot.transfer_ownership(group_id, new_owner_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Userbot Service läuft"}

@app.post("/stop")
async def stop_userbot():
    return await userbot.stop()

@app.get("/status")
async def get_status():
    return await userbot.get_status()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("shutdown")
async def shutdown_event():
    await userbot.stop()

@app.post("/manager/create_session")
async def create_session(data: PhoneNumberRequest):
    return await userbot_manager.create_session(data.phone_number)

@app.post("/manager/send_code")
async def send_code(data: PhoneNumberRequest):
    return await userbot_manager.send_code(data.phone_number)

@app.post("/manager/verify_code")
async def verify_code(data: CodeRequest):
    return await userbot_manager.verify_code(data.phone_number, data.code, data.password)

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
