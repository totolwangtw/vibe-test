"""项目路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _enrich(p: models.Project, db: Session) -> schemas.ProjectOut:
    out = schemas.ProjectOut.model_validate(p)
    out.member_count = db.query(models.ProjectMember).filter_by(project_id=p.id).count()
    out.task_count = db.query(models.Task).filter_by(project_id=p.id).count()
    return out


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    items = db.query(models.Project).order_by(models.Project.id.desc()).all()
    return [_enrich(p, db) for p in items]


@router.get("/{pid}", response_model=schemas.ProjectOut)
def get_project(pid: int, db: Session = Depends(get_db)):
    return _enrich(get_or_404(db, models.Project, pid), db)


@router.post("", response_model=schemas.ProjectOut)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude={"member_ids"})
    p = models.Project(**data)
    db.add(p)
    db.commit()
    db.refresh(p)
    for mid in payload.member_ids:
        db.add(models.ProjectMember(project_id=p.id, member_id=mid))
    db.commit()
    return _enrich(p, db)


@router.put("/{pid}", response_model=schemas.ProjectOut)
def update_project(pid: int, payload: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    p = get_or_404(db, models.Project, pid)
    apply_update(p, payload)
    db.commit()
    db.refresh(p)
    return _enrich(p, db)


@router.delete("/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):
    p = get_or_404(db, models.Project, pid)
    db.delete(p)
    db.commit()
    return {"ok": True}


# ---------- 项目成员管理 ----------
@router.get("/{pid}/members", response_model=list[schemas.MemberOut])
def list_project_members(pid: int, db: Session = Depends(get_db)):
    links = db.query(models.ProjectMember).filter_by(project_id=pid).all()
    return [l.member for l in links]


@router.post("/{pid}/members/{mid}")
def add_project_member(pid: int, mid: int, role: str = None, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    get_or_404(db, models.Member, mid)
    if not db.query(models.ProjectMember).filter_by(project_id=pid, member_id=mid).first():
        db.add(models.ProjectMember(project_id=pid, member_id=mid, role_in_project=role))
        db.commit()
    return {"ok": True}


@router.delete("/{pid}/members/{mid}")
def remove_project_member(pid: int, mid: int, db: Session = Depends(get_db)):
    link = db.query(models.ProjectMember).filter_by(project_id=pid, member_id=mid).first()
    if link:
        db.delete(link)
        db.commit()
    return {"ok": True}


# ---------- 项目成员假期汇总 ----------
@router.get("/{pid}/holidays", response_model=list[schemas.HolidayOut])
def project_holidays(pid: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    return db.query(models.Holiday).filter(
        (models.Holiday.project_id == pid) | (models.Holiday.project_id.is_(None))
    ).all()
