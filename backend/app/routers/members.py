"""成员路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=list[schemas.MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.query(models.Member).order_by(models.Member.id).all()


@router.post("", response_model=schemas.MemberOut)
def create_member(payload: schemas.MemberCreate, db: Session = Depends(get_db)):
    m = models.Member(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/{mid}", response_model=schemas.MemberOut)
def update_member(mid: int, payload: schemas.MemberUpdate, db: Session = Depends(get_db)):
    m = get_or_404(db, models.Member, mid)
    apply_update(m, payload)
    db.commit()
    db.refresh(m)
    return m


@router.delete("/{mid}")
def delete_member(mid: int, db: Session = Depends(get_db)):
    m = get_or_404(db, models.Member, mid)
    db.delete(m)
    db.commit()
    return {"ok": True}
