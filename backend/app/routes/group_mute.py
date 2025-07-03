from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import GroupMute
from app.schemas import GroupMuteCreate, GroupMuteOut
from datetime import datetime, timedelta
from typing import List

router = APIRouter(
    prefix="/group_mutes",
    tags=["group_mutes"]
)

@router.post("/", response_model=GroupMuteOut)
def create_group_mute(mute: GroupMuteCreate, db: Session = Depends(get_db)):
    db_mute = GroupMute(
        user_id=mute.user_id,
        group_id=mute.group_id,
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(seconds=mute.duration_seconds),
        reason=mute.reason,
        issued_by=mute.issued_by,
        active=True,
        timestamp=datetime.utcnow()
    )
    db.add(db_mute)
    db.commit()
    db.refresh(db_mute)
    return db_mute

@router.get("/", response_model=List[GroupMuteOut])
def get_mutes(user_id: int = None, group_id: int = None, db: Session = Depends(get_db)):
    query = db.query(GroupMute)
    if user_id:
        query = query.filter(GroupMute.user_id == user_id)
    if group_id:
        query = query.filter(GroupMute.group_id == group_id)
    return query.order_by(GroupMute.timestamp.desc()).all() 