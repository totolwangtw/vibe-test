"""任务路由 - 含多层级、甘特图数据"""
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.crud import get_or_404, apply_update

router = APIRouter(prefix="/api", tags=["tasks"])


def _sync_tags(task: models.Task, tags: list[dict], db: Session) -> None:
    db.query(models.TaskTag).filter_by(task_id=task.id).delete()
    for t in tags or []:
        db.add(models.TaskTag(
            task_id=task.id,
            name=t.get("name", ""),
            color=t.get("color", "#909399"),
        ))


def _task_to_out(task: models.Task, db: Session) -> schemas.TaskOut:
    out = schemas.TaskOut.model_validate(task)
    if task.owner:
        out.owner = schemas.MemberOut.model_validate(task.owner)
    out.tags = [schemas.TagOut(id=t.id, name=t.name, color=t.color) for t in task.tags]
    out.attachments = [schemas.AttachmentOut.model_validate(a) for a in task.attachments]
    # 递归构建子任务
    out.children = [_task_to_out(c, db) for c in sorted(task.children, key=lambda x: x.sort_order)]
    return out


# ---------- 树形（含子任务） ----------
@router.get("/projects/{pid}/tasks/tree", response_model=list[schemas.TaskOut])
def task_tree(pid: int, db: Session = Depends(get_db)):
    """获取项目任务的多级树（仅返回 parent_id is None 的根任务，递归包含子任务）"""
    get_or_404(db, models.Project, pid)
    roots = db.query(models.Task).filter(
        models.Task.project_id == pid, models.Task.parent_id.is_(None)
    ).order_by(models.Task.sort_order).all()
    return [_task_to_out(t, db) for t in roots]


# ---------- 列表（扁平） ----------
@router.get("/projects/{pid}/tasks", response_model=list[schemas.TaskOut])
def list_tasks(pid: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    items = db.query(models.Task).filter_by(project_id=pid).order_by(models.Task.sort_order).all()
    return [_task_to_out(t, db) for t in items]


# ---------- 单个 ----------
@router.get("/tasks/{tid}", response_model=schemas.TaskOut)
def get_task(tid: int, db: Session = Depends(get_db)):
    return _task_to_out(get_or_404(db, models.Task, tid), db)


# ---------- 创建 ----------
@router.post("/tasks", response_model=schemas.TaskOut, status_code=201)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, payload.project_id)
    data = payload.model_dump(exclude={"tags"})
    tags = payload.tags
    task = models.Task(**data)
    db.add(task)
    db.commit()
    db.refresh(task)
    _sync_tags(task, tags, db)
    db.commit()
    db.refresh(task)
    return _task_to_out(task, db)


# ---------- 更新 ----------
@router.put("/tasks/{tid}", response_model=schemas.TaskOut)
def update_task(tid: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = get_or_404(db, models.Task, tid)
    data = payload.model_dump(exclude_unset=True)
    tags = data.pop("tags", None)
    for k, v in data.items():
        setattr(task, k, v)
    if tags is not None:
        _sync_tags(task, tags, db)
    db.commit()
    db.refresh(task)
    return _task_to_out(task, db)


# ---------- 批量更新排序/层级（拖拽） ----------
@router.put("/projects/{pid}/tasks/batch")
def batch_update_tasks(pid: int, items: list[dict], db: Session = Depends(get_db)):
    """批量更新任务的 parent_id 和 sort_order，用于前端拖拽排序"""
    for item in items:
        t = db.get(models.Task, item["id"])
        if not t or t.project_id != pid:
            continue
        if "parent_id" in item:
            t.parent_id = item["parent_id"]
        if "sort_order" in item:
            t.sort_order = item["sort_order"]
        if "start_date" in item and item["start_date"]:
            t.start_date = datetime.fromisoformat(item["start_date"]).date()
        if "end_date" in item and item["end_date"]:
            t.end_date = datetime.fromisoformat(item["end_date"]).date()
        if "progress" in item:
            t.progress = item["progress"]
    db.commit()
    return {"ok": True}


# ---------- 删除 ----------
@router.delete("/tasks/{tid}")
def delete_task(tid: int, db: Session = Depends(get_db)):
    t = get_or_404(db, models.Task, tid)
    db.delete(t)
    db.commit()
    return {"ok": True}


# ---------- 工时 ----------
@router.post("/tasks/{tid}/worklogs", response_model=schemas.WorkLogOut)
def add_worklog(tid: int, payload: schemas.WorkLogCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Task, tid)
    payload.task_id = tid
    wl = models.WorkLog(**payload.model_dump())
    db.add(wl)
    # 同步实际工时
    task = db.get(models.Task, tid)
    if task:
        from sqlalchemy import select, func as _f
        total = db.query(_f.sum(models.WorkLog.hours)).filter_by(task_id=tid).scalar() or 0
        task.actual_hours = float(total)
    db.commit()
    db.refresh(wl)
    return wl


@router.get("/tasks/{tid}/worklogs", response_model=list[schemas.WorkLogOut])
def list_worklogs(tid: int, db: Session = Depends(get_db)):
    return db.query(models.WorkLog).filter_by(task_id=tid).order_by(models.WorkLog.log_date.desc()).all()


# ---------- 甘特图数据（dhtmlxGantt 兼容） ----------
@router.get("/projects/{pid}/gantt", response_model=schemas.GanttData)
def gantt_data(pid: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Project, pid)
    tasks = db.query(models.Task).filter_by(project_id=pid).order_by(models.Task.sort_order).all()
    gtasks: list[schemas.GanttTask] = []
    for t in tasks:
        if not t.start_date or not t.end_date:
            continue
        duration = max(1, (t.end_date - t.start_date).days + 1)
        owner_name = t.owner.name if t.owner else None
        gtasks.append(schemas.GanttTask(
            id=t.id,
            text=t.title,
            start_date=t.start_date.strftime("%Y-%m-%d %H:%M"),
            duration=duration,
            progress=t.progress / 100.0,
            parent=t.parent_id or 0,
            priority=t.priority,
            owner_id=t.owner_id,
            owner_name=owner_name,
            status=t.status,
            color=t.color,
            open=not t.collapsed,
        ))
    # 简单依赖：当前任务的开始 < 上一个任务的结束时不需要 link；
    # 这里根据 start_date 顺序生成 FS 链接（按同父级顺序）
    links: list[schemas.GanttLink] = []
    by_parent: dict[int, list[models.Task]] = {}
    for t in tasks:
        by_parent.setdefault(t.parent_id or 0, []).append(t)
    for parent_id, group in by_parent.items():
        group.sort(key=lambda x: (x.start_date or date.today(), x.sort_order))
        for i in range(len(group) - 1):
            a, b = group[i], group[i + 1]
            if a.end_date and b.start_date:
                links.append(schemas.GanttLink(
                    id=len(links) + 1, source=a.id, target=b.id, type="0"
                ))
    return schemas.GanttData(tasks=gtasks, links=links)


# 甘特图任务更新（拖拽、改期）
class GanttTaskUpdate(BaseModel):
    id: int
    text: Optional[str] = None
    start_date: Optional[str] = None
    duration: Optional[int] = None
    progress: Optional[float] = None
    parent: Optional[int] = None


@router.put("/projects/{pid}/gantt")
def update_gantt_task(pid: int, payload: GanttTaskUpdate, db: Session = Depends(get_db)):
    t = get_or_404(db, models.Task, payload.id)
    if t.project_id != pid:
        raise HTTPException(403, "任务不属于该项目")
    if payload.start_date:
        try:
            t.start_date = datetime.strptime(payload.start_date[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    if payload.duration is not None:
        if t.start_date:
            t.end_date = t.start_date + timedelta(days=max(1, payload.duration) - 1)
    if payload.progress is not None:
        t.progress = int(payload.progress * 100)
    if payload.parent is not None:
        t.parent_id = payload.parent or None
    if payload.text is not None:
        t.title = payload.text
    db.commit()
    return {"ok": True}
