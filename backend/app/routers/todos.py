"""待办路由"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update

router = APIRouter(prefix="/api", tags=["todos"])


def _enrich(t: models.Todo, db: Session) -> schemas.TodoOut:
    out = schemas.TodoOut.model_validate(t)
    if t.assignee:
        out.assignee = schemas.MemberOut.model_validate(t.assignee)
    # @ 提及
    mentions = db.query(models.Member).filter(models.Member.id.in_(t.mention_ids or [])).all()
    out.mentions = [schemas.MemberOut.model_validate(m) for m in mentions]
    return out


@router.get("/projects/{pid}/todos", response_model=list[schemas.TodoOut])
def list_todos(pid: int, status: str = None, db: Session = Depends(get_db)):
    q = db.query(models.Todo).filter_by(project_id=pid)
    if status:
        q = q.filter(models.Todo.status == status)
    items = q.order_by(models.Todo.created_at.desc()).all()
    return [_enrich(t, db) for t in items]


@router.post("/todos", response_model=schemas.TodoOut, status_code=201)
def create_todo(payload: schemas.TodoCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id)
    t = models.Todo(**payload.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return _enrich(t, db)


@router.get("/todos/{tid}", response_model=schemas.TodoOut)
def get_todo(tid: int, db: Session = Depends(get_db)):
    return _enrich(get_or_404(db, models.Todo, tid), db)


@router.put("/todos/{tid}", response_model=schemas.TodoOut)
def update_todo(tid: int, payload: schemas.TodoUpdate, db: Session = Depends(get_db)):
    t = get_or_404(db, models.Todo, tid)
    apply_update(t, payload)
    db.commit()
    db.refresh(t)
    return _enrich(t, db)


@router.delete("/todos/{tid}")
def delete_todo(tid: int, db: Session = Depends(get_db)):
    t = get_or_404(db, models.Todo, tid)
    db.delete(t)
    db.commit()
    return {"ok": True}


# ---------- @ 提及快捷查询：所有可被@的人 ----------
@router.get("/todos/mention-candidates", response_model=list[schemas.MemberOut])
def mention_candidates(db: Session = Depends(get_db)):
    return db.query(models.Member).order_by(models.Member.name).all()
