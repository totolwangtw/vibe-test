"""问题管理路由"""
from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update
from app.csv_utils import export_csv, parse_csv

router = APIRouter(prefix="/api", tags=["issues"])

CSV_FIELDS = [
    ("id", "ID"),
    ("title", "标题"),
    ("issue_type", "问题类型"),
    ("status", "状态"),
    ("priority", "优先级"),
    ("owner_id", "负责人ID"),
    ("raised_date", "提出日期"),
    ("due_date", "截止日期"),
    ("description_html", "问题描述"),
    ("resolution_html", "解决方案"),
]


def _enrich(i: models.Issue) -> schemas.IssueOut:
    out = schemas.IssueOut.model_validate(i)
    if i.owner:
        out.owner = schemas.MemberOut.model_validate(i.owner)
    return out


@router.get("/projects/{pid}/issues", response_model=list[schemas.IssueOut])
def list_issues(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Issue).filter_by(project_id=pid).order_by(models.Issue.id.desc()).all()
    return [_enrich(i) for i in items]


@router.post("/issues", response_model=schemas.IssueOut, status_code=201)
def create_issue(payload: schemas.IssueCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id)
    i = models.Issue(**payload.model_dump())
    db.add(i)
    db.commit()
    db.refresh(i)
    return _enrich(i)


@router.get("/issues/{iid}", response_model=schemas.IssueOut)
def get_issue(iid: int, db: Session = Depends(get_db)):
    return _enrich(get_or_404(db, models.Issue, iid))


@router.put("/issues/{iid}", response_model=schemas.IssueOut)
def update_issue(iid: int, payload: schemas.IssueUpdate, db: Session = Depends(get_db)):
    i = get_or_404(db, models.Issue, iid)
    apply_update(i, payload)
    db.commit()
    db.refresh(i)
    return _enrich(i)


@router.delete("/issues/{iid}")
def delete_issue(iid: int, db: Session = Depends(get_db)):
    i = get_or_404(db, models.Issue, iid)
    db.delete(i)
    db.commit()
    return {"ok": True}


@router.get("/projects/{pid}/issues/export.csv")
def export_issues_csv(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Issue).filter_by(project_id=pid).order_by(models.Issue.id).all()
    text = export_csv(items, CSV_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="issues_project_{pid}.csv"'},
    )


@router.post("/projects/{pid}/issues/import.csv", response_model=list[schemas.IssueOut])
async def import_issues_csv(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    rows = parse_csv(content, CSV_FIELDS)
    result = []
    for row in rows:
        existing_id = row.pop("id", None)
        existing = db.get(models.Issue, existing_id) if existing_id else None
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            db.commit()
            db.refresh(existing)
            result.append(_enrich(existing))
        else:
            i = models.Issue(project_id=pid, **row)
            db.add(i)
            db.commit()
            db.refresh(i)
            result.append(_enrich(i))
    return result
