from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import GroupWarning, User, Group
from app.schemas import GroupWarningCreate, GroupWarningOut
from datetime import datetime
from typing import List

router = APIRouter(
    prefix="/group_warnings",
    tags=["group_warnings"]
)

@router.post("/", response_model=GroupWarningOut)
def create_group_warning(warning: GroupWarningCreate, db: Session = Depends(get_db)):
    db_warning = GroupWarning(
        user_id=warning.user_id,
        group_id=warning.group_id,
        reason=warning.reason,
        issued_by=warning.issued_by,
        timestamp=datetime.utcnow()
    )
    db.add(db_warning)
    db.commit()
    db.refresh(db_warning)
    return db_warning

@router.get("/", response_model=List[GroupWarningOut])
def get_warnings(user_id: int = None, group_id: int = None, db: Session = Depends(get_db)):
    query = db.query(GroupWarning)
    if user_id:
        query = query.filter(GroupWarning.user_id == user_id)
    if group_id:
        query = query.filter(GroupWarning.group_id == group_id)
    return query.order_by(GroupWarning.timestamp.desc()).all() 