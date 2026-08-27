"""会议记录路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update

router = APIRouter(prefix="/api", tags=["meetings"])


def _enrich(m: models.Meeting, db: Session) -> schemas.MeetingOut:
    out = schemas.MeetingOut.model_validate(m)
    if m.host:
        out.host = schemas.MemberOut.model_validate(m.host)
    out.todo_count = db.query(models.Todo).filter_by(meeting_id=m.id).count()
    return out


@router.get("/projects/{pid}/meetings", response_model=list[schemas.MeetingOut])
def list_meetings(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Meeting).filter_by(project_id=pid).order_by(models.Meeting.meeting_date.desc()).all()
    return [_enrich(m, db) for m in items]


@router.post("/meetings", response_model=schemas.MeetingOut, status_code=201)
def create_meeting(payload: schemas.MeetingCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id)
    m = models.Meeting(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return _enrich(m, db)


@router.get("/meetings/{mid}", response_model=schemas.MeetingOut)
def get_meeting(mid: int, db: Session = Depends(get_db)):
    return _enrich(get_or_404(db, models.Meeting, mid), db)


@router.put("/meetings/{mid}", response_model=schemas.MeetingOut)
def update_meeting(mid: int, payload: schemas.MeetingUpdate, db: Session = Depends(get_db)):
    m = get_or_404(db, models.Meeting, mid)
    apply_update(m, payload)
    db.commit()
    db.refresh(m)
    return _enrich(m, db)


@router.delete("/meetings/{mid}")
def delete_meeting(mid: int, db: Session = Depends(get_db)):
    m = get_or_404(db, models.Meeting, mid)
    db.delete(m)
    db.commit()
    return {"ok": True}
