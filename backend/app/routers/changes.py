"""变更管理路由"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update
from app.csv_utils import export_csv, parse_csv

router = APIRouter(prefix="/api", tags=["changes"])

# CSV 字段：(字段名, 显示列名)
CSV_FIELDS = [
    ("id", "ID"),
    ("title", "标题"),
    ("change_type", "变更类型"),
    ("status", "状态"),
    ("impact_level", "影响等级"),
    ("requester_id", "申请人ID"),
    ("owner_id", "负责人ID"),
    ("request_date", "申请日期"),
    ("plan_date", "计划日期"),
    ("implement_date", "实施日期"),
    ("content_html", "变更描述"),
    ("impact_html", "影响范围"),
    ("rollback_html", "回滚方案"),
]


def _enrich(c: models.Change) -> schemas.ChangeOut:
    out = schemas.ChangeOut.model_validate(c)
    if c.requester:
        out.requester = schemas.MemberOut.model_validate(c.requester)
    if c.owner:
        out.owner = schemas.MemberOut.model_validate(c.owner)
    return out


@router.get("/projects/{pid}/changes", response_model=list[schemas.ChangeOut])
def list_changes(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Change).filter_by(project_id=pid).order_by(models.Change.id.desc()).all()
    return [_enrich(c) for c in items]


@router.post("/changes", response_model=schemas.ChangeOut, status_code=201)
def create_change(payload: schemas.ChangeCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id)
    c = models.Change(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return _enrich(c)


@router.get("/changes/{cid}", response_model=schemas.ChangeOut)
def get_change(cid: int, db: Session = Depends(get_db)):
    return _enrich(get_or_404(db, models.Change, cid))


@router.put("/changes/{cid}", response_model=schemas.ChangeOut)
def update_change(cid: int, payload: schemas.ChangeUpdate, db: Session = Depends(get_db)):
    c = get_or_404(db, models.Change, cid)
    apply_update(c, payload)
    db.commit()
    db.refresh(c)
    return _enrich(c)


@router.delete("/changes/{cid}")
def delete_change(cid: int, db: Session = Depends(get_db)):
    c = get_or_404(db, models.Change, cid)
    db.delete(c)
    db.commit()
    return {"ok": True}


# ---------- CSV 导入导出 ----------
@router.get("/projects/{pid}/changes/export.csv")
def export_changes_csv(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Change).filter_by(project_id=pid).order_by(models.Change.id).all()
    text = export_csv(items, CSV_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="changes_project_{pid}.csv"'},
    )


@router.post("/projects/{pid}/changes/import.csv", response_model=list[schemas.ChangeOut])
async def import_changes_csv(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    rows = parse_csv(content, CSV_FIELDS)
    result: list[schemas.ChangeOut] = []
    for row in rows:
        # id 仅用于更新匹配，不强制
        existing_id = row.pop("id", None)
        existing = None
        if existing_id:
            existing = db.get(models.Change, existing_id)
        row["project_id"] = pid
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            db.commit()
            db.refresh(existing)
            result.append(_enrich(existing))
        else:
            row.pop("project_id", None)
            c = models.Change(project_id=pid, **row)
            db.add(c)
            db.commit()
            db.refresh(c)
            result.append(_enrich(c))
    return result
