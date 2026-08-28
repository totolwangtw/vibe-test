"""Pydantic 输入/输出 Schema"""
from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- 通用 ----------
class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IdOut(BaseModel):
    id: int


# ---------- 成员 ----------
class MemberBase(BaseModel):
    name: str
    avatar_color: str = "#409EFF"
    email: Optional[str] = None
    role: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    avatar_color: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None


class MemberOut(MemberBase, ORM):
    id: int
    created_at: Optional[datetime] = None


# ---------- 项目 ----------
class ProjectBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    priority: str = "P2"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    color: str = "#409EFF"


class ProjectCreate(ProjectBase):
    member_ids: list[int] = []


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    color: Optional[str] = None
    progress: Optional[int] = None


class ProjectOut(ProjectBase, ORM):
    id: int
    progress: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    member_count: int = 0
    task_count: int = 0


# ---------- 任务 ----------
class TaskBase(BaseModel):
    title: str
    content_html: Optional[str] = None
    status: str = "todo"
    priority: str = "P2"
    task_type: str = "task"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_hours: float = 0
    actual_hours: float = 0
    progress: int = 0
    owner_id: Optional[int] = None
    parent_id: Optional[int] = None
    sort_order: int = 0
    is_starred: bool = False
    color: Optional[str] = None
    collapsed: bool = False
    tags: list[dict] = []  # [{"name":"...", "color":"..."}]


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    content_html: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    task_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    planned_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    progress: Optional[int] = None
    owner_id: Optional[int] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_starred: Optional[bool] = None
    color: Optional[str] = None
    collapsed: Optional[bool] = None
    tags: Optional[list[dict]] = None


class TagOut(BaseModel):
    id: int
    name: str
    color: str


class AttachmentOut(BaseModel):
    id: int
    filename: str
    size: int
    mime_type: Optional[str]
    uploaded_at: Optional[datetime]


class TaskOut(ORM):
    id: int
    project_id: int
    parent_id: Optional[int]
    title: str
    content_html: Optional[str]
    status: str
    priority: str
    task_type: str
    start_date: Optional[date]
    end_date: Optional[date]
    planned_hours: float
    actual_hours: float
    progress: int
    owner_id: Optional[int]
    owner: Optional[MemberOut] = None
    sort_order: int
    is_starred: bool
    color: Optional[str]
    collapsed: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    children: list["TaskOut"] = []
    attachments: list[AttachmentOut] = []
    tags: list[TagOut] = []


# 前置声明
TaskOut.model_rebuild()


# 甘特图任务（dhtmlxGantt 兼容）
class GanttLink(BaseModel):
    id: int
    source: int
    target: int
    type: str = "0"  # 0=FS, 1=SS, 2=SF, 3=FF


class GanttTask(BaseModel):
    id: int
    text: str
    start_date: str
    duration: int = 1
    progress: float = 0
    parent: int = 0
    priority: Optional[str] = None
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    status: Optional[str] = None
    color: Optional[str] = None
    open: bool = True


class GanttData(BaseModel):
    tasks: list[GanttTask]
    links: list[GanttLink]


# ---------- 工时记录 ----------
class WorkLogCreate(BaseModel):
    task_id: int
    member_id: Optional[int] = None
    hours: float
    log_date: Optional[date] = None
    comment: Optional[str] = None


class WorkLogOut(ORM):
    id: int
    task_id: int
    member_id: Optional[int]
    hours: float
    log_date: Optional[date]
    comment: Optional[str]


# ---------- 会议 ----------
class MeetingBase(BaseModel):
    title: str
    meeting_type: str = "daily"  # daily / weekly
    meeting_date: date
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    host_id: Optional[int] = None
    attendees: list[int] = []
    content_html: Optional[str] = None


class MeetingCreate(MeetingBase):
    project_id: int


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    meeting_type: Optional[str] = None
    meeting_date: Optional[date] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    host_id: Optional[int] = None
    attendees: Optional[list[int]] = None
    content_html: Optional[str] = None


class MeetingOut(ORM):
    id: int
    project_id: int
    title: str
    meeting_type: str
    meeting_date: date
    start_time: Optional[str]
    end_time: Optional[str]
    host_id: Optional[int]
    host: Optional[MemberOut] = None
    attendees: list[int]
    content_html: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    todo_count: int = 0


# ---------- 待办 ----------
class TodoBase(BaseModel):
    title: str
    content: Optional[str] = None
    mention_ids: list[int] = []
    assignee_id: Optional[int] = None
    status: str = "open"
    priority: str = "P2"
    due_date: Optional[date] = None


class TodoCreate(TodoBase):
    project_id: int
    meeting_id: Optional[int] = None


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mention_ids: Optional[list[int]] = None
    assignee_id: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None


class TodoOut(ORM):
    id: int
    project_id: int
    meeting_id: Optional[int]
    title: str
    content: Optional[str]
    mention_ids: list[int]
    assignee_id: Optional[int]
    assignee: Optional[MemberOut] = None
    mentions: list[MemberOut] = []
    status: str
    priority: str
    due_date: Optional[date]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ---------- 假期 ----------
class HolidayBase(BaseModel):
    member_id: int
    project_id: Optional[int] = None
    holiday_type: str = "personal"
    start_date: date
    end_date: date
    note: Optional[str] = None


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(BaseModel):
    holiday_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    note: Optional[str] = None
    project_id: Optional[int] = None


class HolidayOut(ORM):
    id: int
    member_id: int
    member: Optional[MemberOut] = None
    project_id: Optional[int]
    holiday_type: str
    start_date: date
    end_date: date
    note: Optional[str]
    created_at: Optional[datetime]


# ---------- 变更管理 ----------
class ChangeBase(BaseModel):
    title: str
    content_html: Optional[str] = None
    change_type: str = "standard"
    status: str = "draft"
    impact_level: str = "M"
    requester_id: Optional[int] = None
    owner_id: Optional[int] = None
    request_date: Optional[date] = None
    plan_date: Optional[date] = None
    implement_date: Optional[date] = None
    impact_html: Optional[str] = None
    rollback_html: Optional[str] = None


class ChangeCreate(ChangeBase):
    project_id: int


class ChangeUpdate(BaseModel):
    title: Optional[str] = None
    content_html: Optional[str] = None
    change_type: Optional[str] = None
    status: Optional[str] = None
    impact_level: Optional[str] = None
    requester_id: Optional[int] = None
    owner_id: Optional[int] = None
    request_date: Optional[date] = None
    plan_date: Optional[date] = None
    implement_date: Optional[date] = None
    impact_html: Optional[str] = None
    rollback_html: Optional[str] = None


class ChangeOut(ORM):
    id: int
    project_id: int
    title: str
    content_html: Optional[str]
    change_type: str
    status: str
    impact_level: str
    requester_id: Optional[int]
    requester: Optional[MemberOut] = None
    owner_id: Optional[int]
    owner: Optional[MemberOut] = None
    request_date: Optional[date]
    plan_date: Optional[date]
    implement_date: Optional[date]
    impact_html: Optional[str]
    rollback_html: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ---------- 风险管理 ----------
class RiskBase(BaseModel):
    title: str
    description_html: Optional[str] = None
    risk_type: str = "technical"
    probability: str = "M"
    impact: str = "M"
    level: str = "M"
    status: str = "open"
    owner_id: Optional[int] = None
    due_date: Optional[date] = None
    mitigation_html: Optional[str] = None


class RiskCreate(RiskBase):
    project_id: int


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description_html: Optional[str] = None
    risk_type: Optional[str] = None
    probability: Optional[str] = None
    impact: Optional[str] = None
    level: Optional[str] = None
    status: Optional[str] = None
    owner_id: Optional[int] = None
    due_date: Optional[date] = None
    mitigation_html: Optional[str] = None


class RiskOut(ORM):
    id: int
    project_id: int
    title: str
    description_html: Optional[str]
    risk_type: str
    probability: str
    impact: str
    level: str
    status: str
    owner_id: Optional[int]
    owner: Optional[MemberOut] = None
    due_date: Optional[date]
    mitigation_html: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ---------- 问题管理 ----------
class IssueBase(BaseModel):
    title: str
    description_html: Optional[str] = None
    issue_type: str = "technical"
    status: str = "open"
    priority: str = "P2"
    owner_id: Optional[int] = None
    raised_date: Optional[date] = None
    due_date: Optional[date] = None
    resolution_html: Optional[str] = None


class IssueCreate(IssueBase):
    project_id: int


class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description_html: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    owner_id: Optional[int] = None
    raised_date: Optional[date] = None
    due_date: Optional[date] = None
    resolution_html: Optional[str] = None


class IssueOut(ORM):
    id: int
    project_id: int
    title: str
    description_html: Optional[str]
    issue_type: str
    status: str
    priority: str
    owner_id: Optional[int]
    owner: Optional[MemberOut] = None
    raised_date: Optional[date]
    due_date: Optional[date]
    resolution_html: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


# ---------- Dashboard ----------
class DashboardOverview(BaseModel):
    project_count: int
    active_project_count: int
    task_count: int
    done_task_count: int
    in_progress_count: int
    overdue_count: int
    total_planned_hours: float
    total_actual_hours: float
    member_count: int
    open_todo_count: int


class ProjectStatusItem(BaseModel):
    id: int
    name: str
    code: Optional[str]
    status: str
    priority: str
    progress: int
    color: str
    task_count: int
    done_task_count: int
    overdue_count: int
    end_date: Optional[date]


class DashboardData(BaseModel):
    overview: DashboardOverview
    projects: list[ProjectStatusItem]
    priority_distribution: dict[str, int]
    status_distribution: dict[str, int]
    upcoming_todos: list[TodoOut]
    recent_meetings: list[MeetingOut]
