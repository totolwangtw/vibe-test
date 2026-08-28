"""为已有模块补充 CSV 导入导出端点"""
from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.crud import get_or_404
from app.csv_utils import export_csv, parse_csv

router = APIRouter(prefix="/api", tags=["csv"])


# ---------- 任务 ----------
TASK_FIELDS = [
    ("id", "ID"),
    ("title", "标题"),
    ("status", "状态"),
    ("priority", "优先级"),
    ("task_type", "类型"),
    ("start_date", "开始日期"),
    ("end_date", "结束日期"),
    ("planned_hours", "计划工时"),
    ("actual_hours", "实际工时"),
    ("progress", "进度"),
    ("owner_id", "负责人ID"),
    ("parent_id", "父任务ID"),
    ("sort_order", "排序"),
    ("is_starred", "星标"),
    ("content_html", "业务需求"),
]


@router.get("/projects/{pid}/tasks/export.csv")
def export_tasks_csv(pid: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    items = db.query(models.Task).filter_by(project_id=pid).order_by(models.Task.sort_order).all()
    text = export_csv(items, TASK_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="tasks_project_{pid}.csv"'},
    )


@router.post("/projects/{pid}/tasks/import.csv")
async def import_tasks_csv(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    rows = parse_csv(content, TASK_FIELDS)
    count = 0
    for row in rows:
        existing_id = row.pop("id", None)
        existing = db.get(models.Task, existing_id) if existing_id else None
        row["project_id"] = pid
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            db.commit()
        else:
            t = models.Task(**row)
            db.add(t)
            db.commit()
        count += 1
    return {"imported": count}


# ---------- 待办 ----------
TODO_FIELDS = [
    ("id", "ID"),
    ("title", "标题"),
    ("content", "内容"),
    ("assignee_id", "责任人ID"),
    ("status", "状态"),
    ("priority", "优先级"),
    ("due_date", "截止日期"),
]


@router.get("/projects/{pid}/todos/export.csv")
def export_todos_csv(pid: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    items = db.query(models.Todo).filter_by(project_id=pid).order_by(models.Todo.id).all()
    text = export_csv(items, TODO_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="todos_project_{pid}.csv"'},
    )


@router.post("/projects/{pid}/todos/import.csv")
async def import_todos_csv(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    rows = parse_csv(content, TODO_FIELDS)
    count = 0
    for row in rows:
        existing_id = row.pop("id", None)
        existing = db.get(models.Todo, existing_id) if existing_id else None
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            db.commit()
        else:
            t = models.Todo(project_id=pid, **row)
            db.add(t)
            db.commit()
        count += 1
    return {"imported": count}


# ---------- 会议 ----------
MEETING_FIELDS = [
    ("id", "ID"),
    ("title", "主题"),
    ("meeting_type", "类型"),
    ("meeting_date", "日期"),
    ("start_time", "开始时间"),
    ("end_time", "结束时间"),
    ("host_id", "主持人ID"),
    ("content_html", "会议纪要"),
]


@router.get("/projects/{pid}/meetings/export.csv")
def export_meetings_csv(pid: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    items = db.query(models.Meeting).filter_by(project_id=pid).order_by(models.Meeting.id).all()
    text = export_csv(items, MEETING_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="meetings_project_{pid}.csv"'},
    )


# ---------- 成员 ----------
MEMBER_FIELDS = [
    ("id", "ID"),
    ("name", "姓名"),
    ("role", "角色"),
    ("email", "邮箱"),
    ("avatar_color", "头像颜色"),
]


@router.get("/members/export.csv")
def export_members_csv(db: Session = Depends(get_db)):
    items = db.query(models.Member).order_by(models.Member.id).all()
    text = export_csv(items, MEMBER_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="members.csv"'},
    )


@router.post("/members/import.csv")
async def import_members_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    rows = parse_csv(content, MEMBER_FIELDS)
    count = 0
    for row in rows:
        existing_id = row.pop("id", None)
        existing = db.get(models.Member, existing_id) if existing_id else None
        if existing:
            for k, v in row.items():
                setattr(existing, k, v)
            db.commit()
        else:
            m = models.Member(**row)
            db.add(m)
            db.commit()
        count += 1
    return {"imported": count}


# ---------- 假期 ----------
HOLIDAY_FIELDS = [
    ("id", "ID"),
    ("member_id", "成员ID"),
    ("project_id", "项目ID"),
    ("holiday_type", "类型"),
    ("start_date", "开始日期"),
    ("end_date", "结束日期"),
    ("note", "备注"),
]


@router.get("/holidays/export.csv")
def export_holidays_csv(db: Session = Depends(get_db)):
    items = db.query(models.Holiday).order_by(models.Holiday.id).all()
    text = export_csv(items, HOLIDAY_FIELDS)
    return Response(
        content=text,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="holidays.csv"'},
    )
