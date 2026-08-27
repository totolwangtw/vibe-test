"""假期路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update

router = APIRouter(prefix="/api/holidays", tags=["holidays"])


def _enrich(h: models.Holiday) -> schemas.HolidayOut:
    out = schemas.HolidayOut.model_validate(h)
    if h.member:
        out.member = schemas.MemberOut.model_validate(h.member)
    return out


@router.get("", response_model=list[schemas.HolidayOut])
def list_holidays(member_id: int = None, project_id: int = None, db: Session = Depends(get_db)):
    q = db.query(models.Holiday)
    if member_id is not None:
        q = q.filter(models.Holiday.member_id == member_id)
    if project_id is not None:
        q = q.filter((models.Holiday.project_id == project_id) | (models.Holiday.project_id.is_(None)))
    items = q.order_by(models.Holiday.start_date.desc()).all()
    return [_enrich(h) for h in items]


@router.post("", response_model=schemas.HolidayOut, status_code=201)
def create_holiday(payload: schemas.HolidayCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Member, payload.member_id)
    h = models.Holiday(**payload.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return _enrich(h)


@router.put("/{hid}", response_model=schemas.HolidayOut)
def update_holiday(hid: int, payload: schemas.HolidayUpdate, db: Session = Depends(get_db)):
    h = get_or_404(db, models.Holiday, hid)
    apply_update(h, payload)
    db.commit()
    db.refresh(h)
    return _enrich(h)


@router.delete("/{hid}")
def delete_holiday(hid: int, db: Session = Depends(get_db)):
    h = get_or_404(db, models.Holiday, hid)
    db.delete(h)
    db.commit()
    return {"ok": True}
