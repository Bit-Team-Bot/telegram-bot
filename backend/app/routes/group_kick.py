from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import GroupKick
from backend.app.schemas import GroupKickCreate, GroupKickOut
from datetime import datetime
from typing import List, Optional

router = APIRouter(
    prefix="/group_kicks",
    tags=["group_kicks"]
)

@router.post("/", response_model=GroupKickOut)
def create_group_kick(kick: GroupKickCreate, db: Session = Depends(get_db)):
    # Optional: Prüfen, ob User/Group existieren
    db_kick = GroupKick(
        user_id=kick.user_id,
        group_id=kick.group_id,
        reason=kick.reason,
        issued_by=kick.issued_by,
        timestamp=datetime.utcnow()
    )
    db.add(db_kick)
    db.commit()
    db.refresh(db_kick)
    return db_kick

@router.get("/", response_model=List[GroupKickOut])
def get_kicks(user_id: Optional[int] = None, group_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(GroupKick)
    if user_id:
        query = query.filter(GroupKick.user_id == user_id)
    if group_id:
        query = query.filter(GroupKick.group_id == group_id)
    return query.order_by(GroupKick.timestamp.desc()).all() 