from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from app.models import SignalGroup, User
from ..schemas import SignalGroupResponse, SignalGroupCreate, SignalGroupUpdate

router = APIRouter(prefix="/signalgroups", tags=["signalgroups"])

@router.get("/", response_model=List[SignalGroupResponse])
def list_signalgroups(db: Session = Depends(get_db)):
    return db.query(SignalGroup).all()

@router.post("/", response_model=SignalGroupResponse)
def create_signalgroup(data: SignalGroupCreate, db: Session = Depends(get_db)):
    group = SignalGroup(**data.dict())
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

@router.put("/{signalgroup_id}", response_model=SignalGroupResponse)
def update_signalgroup(signalgroup_id: int, data: SignalGroupUpdate, db: Session = Depends(get_db)):
    group = db.query(SignalGroup).filter(SignalGroup.id == signalgroup_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Signalgruppe nicht gefunden")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(group, key, value)
    db.commit()
    db.refresh(group)
    return group

@router.delete("/{signalgroup_id}")
def delete_signalgroup(signalgroup_id: int, db: Session = Depends(get_db)):
    group = db.query(SignalGroup).filter(SignalGroup.id == signalgroup_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Signalgruppe nicht gefunden")
    db.delete(group)
    db.commit()
    return {"status": "ok"}

@router.post("/{signalgroup_id}/assign")
def assign_signalgroup_to_user(signalgroup_id: int, user_id: int, db: Session = Depends(get_db)):
    group = db.query(SignalGroup).filter(SignalGroup.id == signalgroup_id).first()
    user = db.query(User).filter(User.id == user_id).first()
    if not group or not user:
        raise HTTPException(status_code=404, detail="Signalgruppe oder User nicht gefunden")
    # Beispiel: User bekommt ein Subscription-Objekt für die Gruppe
    # (Implementierung je nach Modellstruktur)
    # Hier nur Dummy-Rückgabe:
    return {"status": "ok", "info": "Verknüpfung muss ggf. noch modelliert werden"}