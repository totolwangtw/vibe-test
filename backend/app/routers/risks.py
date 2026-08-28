"""风险管理路由"""
from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update
from app.csv_utils import export_csv, parse_csv

router = APIRouter(prefix="/api", tags=["risks"])

CSV_FIELDS = [
    ("id", "ID"),
    ("title", "标题"),
    ("risk_type", "风险类型"),
    ("probability", "发生概率"),
    ("impact", "影响程度"),
    ("level", "风险等级"),
    ("status", "状态"),
    ("owner_id", "负责人ID"),
    ("due_date", "截止日期"),
    ("description_html", "风险描述"),
    ("mitigation_html", "缓解措施"),
]


def _enrich(r: models.Risk) -> schemas.RiskOut:
    out = schemas.RiskOut.model_validate(r)
    if r.owner:
        out.owner = schemas.MemberOut.model_validate(r.owner)
    return out


@router.get("/projects/{pid}/risks", response_model=list[schemas.RiskOut])
def list_risks(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Risk).filter_by(project_id=pid).order_by(models.Risk.id.desc()).all()
    return [_enrich(r) for r in items]


@router.post("/risks", response_model=schemas.RiskOut, status_code=201)
def create_risk(payload: schemas.RiskCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id)
    r = models.Risk(**payload.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return _enrich(r)


@router.get("/risks/{rid}", response_model=schemas.RiskOut)
def get_risk(rid: int, db: Session = Depends(get_db)):
    return _enrich(get_or_404(db, models.Risk, rid))


@router.put("/risks/{rid}", response_model=schemas.RiskOut)
def update_risk(rid: int, payload: schemas.RiskUpdate, db: Session = Depends(get_db)):
    r = get_or_404(db, models.Risk, rid)
    apply_update(r, payload)
    db.commit()
    db.refresh(r)
    return _enrich(r)


@router.delete("/risks/{rid}")
def delete_risk(rid: int, db: Session = Depends(get_db)):
    r = get_or_404(db, models.Risk, rid)
    db.delete(r)
    db.commit()
    return {"ok": True}


@router.get("/projects/{pid}/risks/export.csv")
def export_risks_csv(pid: int, db: Session = Depends(get_db)):
    items = db.query(models.Risk).filter_by(project_id=pid).order_by(models.Risk.id).all()
    text = export_csv(items, CSV_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="risks_project_{pid}.csv"'},
    )


@router.post("/projects/{pid}/risks/import.csv", response_model=list[schemas.RiskOut])
async def import_risks_csv(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    rows = parse_csv(content, CSV_FIELDS)
    result = []
    for row in rows:
        existing_id = row.pop("id", None)
        existing = db.get(models.Risk, existing_id) if existing_id else None
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            db.commit()
            db.refresh(existing)
            result.append(_enrich(existing))
        else:
            r = models.Risk(project_id=pid, **row)
            db.add(r)
            db.commit()
            db.refresh(r)
            result.append(_enrich(r))
    return result
