"""Dashboard 路由 - 项目总览"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func as _f

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=schemas.DashboardData)
def dashboard(db: Session = Depends(get_db)):
    today = date.today()
    # 概览
    project_count = db.query(_f.count(models.Project.id)).scalar() or 0
    active_project_count = db.query(_f.count(models.Project.id)).filter(models.Project.status == "active").scalar() or 0
    task_count = db.query(_f.count(models.Task.id)).scalar() or 0
    done_task_count = db.query(_f.count(models.Task.id)).filter(models.Task.status == "done").scalar() or 0
    in_progress_count = db.query(_f.count(models.Task.id)).filter(models.Task.status == "doing").scalar() or 0
    overdue_count = db.query(_f.count(models.Task.id)).filter(
        models.Task.end_date < today, models.Task.status != "done"
    ).scalar() or 0
    total_planned = db.query(_f.sum(models.Task.planned_hours)).scalar() or 0
    total_actual = db.query(_f.sum(models.Task.actual_hours)).scalar() or 0
    member_count = db.query(_f.count(models.Member.id)).scalar() or 0
    open_todo_count = db.query(_f.count(models.Todo.id)).filter(models.Todo.status != "done").scalar() or 0

    # 项目状态列表
    projects = db.query(models.Project).order_by(models.Project.id.desc()).all()
    project_items: list[schemas.ProjectStatusItem] = []
    for p in projects:
        task_count_p = db.query(_f.count(models.Task.id)).filter_by(project_id=p.id).scalar() or 0
        done_count_p = db.query(_f.count(models.Task.id)).filter_by(project_id=p.id, status="done").scalar() or 0
        overdue_p = db.query(_f.count(models.Task.id)).filter(
            models.Task.project_id == p.id, models.Task.end_date < today, models.Task.status != "done"
        ).scalar() or 0
        project_items.append(schemas.ProjectStatusItem(
            id=p.id, name=p.name, code=p.code, status=p.status, priority=p.priority,
            progress=p.progress, color=p.color, task_count=task_count_p,
            done_task_count=done_count_p, overdue_count=overdue_p, end_date=p.end_date,
        ))

    # 优先级 / 状态分布
    pri_rows = db.query(models.Task.priority, _f.count(models.Task.id)).group_by(models.Task.priority).all()
    priority_distribution = {p: 0 for p in ["P0", "P1", "P2", "P3"]}
    for p, c in pri_rows:
        priority_distribution[p] = c

    st_rows = db.query(models.Task.status, _f.count(models.Task.id)).group_by(models.Task.status).all()
    status_distribution = {"todo": 0, "doing": 0, "done": 0, "blocked": 0}
    for s, c in st_rows:
        status_distribution[s] = c

    # 待办（未完成 + 即将到期）
    upcoming_todos_rows = db.query(models.Todo).filter(
        models.Todo.status != "done"
    ).order_by(models.Todo.due_date.asc()).limit(10).all()
    upcoming_todos = []
    for t in upcoming_todos_rows:
        out = schemas.TodoOut.model_validate(t)
        if t.assignee:
            out.assignee = schemas.MemberOut.model_validate(t.assignee)
        mentions = db.query(models.Member).filter(models.Member.id.in_(t.mention_ids or [])).all()
        out.mentions = [schemas.MemberOut.model_validate(m) for m in mentions]
        upcoming_todos.append(out)

    # 近期会议
    recent_meetings_rows = db.query(models.Meeting).order_by(
        models.Meeting.meeting_date.desc()
    ).limit(5).all()
    recent_meetings = []
    for m in recent_meetings_rows:
        out = schemas.MeetingOut.model_validate(m)
        if m.host:
            out.host = schemas.MemberOut.model_validate(m.host)
        out.todo_count = db.query(_f.count(models.Todo.id)).filter_by(meeting_id=m.id).scalar() or 0
        recent_meetings.append(out)

    return schemas.DashboardData(
        overview=schemas.DashboardOverview(
            project_count=project_count, active_project_count=active_project_count,
            task_count=task_count, done_task_count=done_task_count,
            in_progress_count=in_progress_count, overdue_count=overdue_count,
            total_planned_hours=float(total_planned), total_actual_hours=float(total_actual),
            member_count=member_count, open_todo_count=open_todo_count,
        ),
        projects=project_items,
        priority_distribution=priority_distribution,
        status_distribution=status_distribution,
        upcoming_todos=upcoming_todos,
        recent_meetings=recent_meetings,
    )


# 单项目仪表盘
@router.get("/projects/{pid}")
def project_dashboard(pid: int, db: Session = Depends(get_db)):
    today = date.today()
    tasks = db.query(models.Task).filter_by(project_id=pid).all()
    by_status = {"todo": 0, "doing": 0, "done": 0, "blocked": 0}
    by_priority = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    by_owner: dict[str, int] = {}
    overdue = 0
    planned_hours = 0
    actual_hours = 0
    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
        if t.owner:
            by_owner[t.owner.name] = by_owner.get(t.owner.name, 0) + 1
        if t.end_date and t.end_date < today and t.status != "done":
            overdue += 1
        planned_hours += t.planned_hours or 0
        actual_hours += t.actual_hours or 0

    todos = db.query(models.Todo).filter_by(project_id=pid).all()
    open_todos = [t for t in todos if t.status != "done"]
    upcoming_meetings = db.query(models.Meeting).filter(
        models.Meeting.project_id == pid, models.Meeting.meeting_date >= today
    ).order_by(models.Meeting.meeting_date.asc()).limit(5).all()

    return {
        "task_total": len(tasks),
        "by_status": by_status,
        "by_priority": by_priority,
        "by_owner": by_owner,
        "overdue": overdue,
        "planned_hours": planned_hours,
        "actual_hours": actual_hours,
        "open_todos": len(open_todos),
        "upcoming_meetings": [
            {"id": m.id, "title": m.title, "date": m.meeting_date.isoformat(),
             "type": m.meeting_type} for m in upcoming_meetings
        ],
    }
