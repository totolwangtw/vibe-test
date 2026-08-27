"""数据模型 - 项目管理工具全部业务实体

设计要点：
- 项目(Project) -> 多个任务(Task)，任务支持多级父子层级(parent_id 自关联)
- 任务 -> 富文本业务需求(content_html)、附件(Attachment)、工时记录、责任人
- 会议记录(Meeting) 区分 日会/周会，关联项目
- 待办(Todo) 跟踪项目，可 @ 责任人(mention_ids)，从会议产出
- 假期(Holiday) 按成员维度记录
- 标签(Tag) 多对多关联任务
- 活动(ActivityLog) 记录关键操作（可选扩展）
"""
from __future__ import annotations

import json
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------- 成员 ----------------
class Member(Base):
    """责任人/项目成员（本地用户体系，无登录，用于 @ 提及和指派）"""

    __tablename__ = "members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, index=True)
    avatar_color = Column(String(16), default="#409EFF")  # 头像底色
    email = Column(String(128), nullable=True)
    role = Column(String(64), nullable=True)  # 角色：PM/前端/后端/测试...
    created_at = Column(DateTime, default=datetime.utcnow)

    holidays = relationship("Holiday", back_populates="member", cascade="all, delete-orphan")
    tasks_owned = relationship("Task", back_populates="owner", foreign_keys="Task.owner_id")


# ---------------- 项目 ----------------
class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, index=True)
    code = Column(String(32), nullable=True, index=True)  # 项目代号
    description = Column(Text, nullable=True)
    status = Column(String(16), default="active")  # active / paused / done
    priority = Column(String(16), default="P2")  # P0/P1/P2/P3
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    color = Column(String(16), default="#409EFF")  # 甘特图项目颜色
    progress = Column(Integer, default=0)  # 整体进度 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    meetings = relationship("Meeting", back_populates="project", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="project", cascade="all, delete-orphan")
    members_link = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")


class ProjectMember(Base):
    """项目-成员 多对多"""
    __tablename__ = "project_members"
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), primary_key=True)
    role_in_project = Column(String(64), nullable=True)  # 在该项目中的角色

    project = relationship("Project", back_populates="members_link")
    member = relationship("Member")


# ---------------- 任务 ----------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True, index=True)  # 多级层级
    title = Column(String(256), nullable=False)
    # 业务需求富文本（HTML）
    content_html = Column(Text, nullable=True)
    # 任务属性
    status = Column(String(16), default="todo")  # todo / doing / done / blocked
    priority = Column(String(16), default="P2")  # P0/P1/P2/P3
    task_type = Column(String(32), default="task")  # task / milestone / bug / story
    # 排期
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    planned_hours = Column(Float, default=0)  # 计划工时
    actual_hours = Column(Float, default=0)  # 实际工时
    progress = Column(Integer, default=0)  # 进度 0-100
    # 责任人
    owner_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    # 排序
    sort_order = Column(Integer, default=0)
    # 标记
    is_starred = Column(Boolean, default=False)  # 星标
    color = Column(String(16), nullable=True)  # 自定义颜色
    # 折叠状态（前端也可保存）
    collapsed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    parent = relationship("Task", remote_side="Task.id", back_populates="children")
    children = relationship("Task", back_populates="parent", cascade="all, delete-orphan")
    owner = relationship("Member", back_populates="tasks_owned", foreign_keys=[owner_id])
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
    tags = relationship("TaskTag", back_populates="task", cascade="all, delete-orphan")
    worklogs = relationship("WorkLog", back_populates="task", cascade="all, delete-orphan")


class TaskTag(Base):
    __tablename__ = "task_tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(32), nullable=False)
    color = Column(String(16), default="#909399")

    task = relationship("Task", back_populates="tags")


class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(256), nullable=False)
    stored_name = Column(String(256), nullable=False)  # 存储文件名（含时间戳防冲突）
    size = Column(Integer, default=0)
    mime_type = Column(String(128), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="attachments")


class WorkLog(Base):
    """工时记录 - 用于追踪实际工时"""
    __tablename__ = "worklogs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    hours = Column(Float, nullable=False)
    log_date = Column(Date, default=date.today)
    comment = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="worklogs")
    member = relationship("Member")


# ---------------- 会议记录 ----------------
class Meeting(Base):
    """日会 / 周会记录"""
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    meeting_type = Column(String(16), default="daily")  # daily / weekly
    meeting_date = Column(Date, default=date.today)
    start_time = Column(String(8), nullable=True)  # "10:00"
    end_time = Column(String(8), nullable=True)
    host_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    attendees = Column(JSON, default=list)  # [member_id, ...]
    content_html = Column(Text, nullable=True)  # 会议纪要富文本
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="meetings")
    host = relationship("Member")
    todos = relationship("Todo", back_populates="meeting", cascade="all, delete-orphan")


# ---------------- 待办 ----------------
class Todo(Base):
    """项目待办 - 由会议产出或日常追踪"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=True)
    # @ 责任人（多个）
    mention_ids = Column(JSON, default=list)  # [member_id, ...]
    assignee_id = Column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(16), default="open")  # open / in_progress / done
    priority = Column(String(16), default="P2")
    due_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="todos")
    meeting = relationship("Meeting", back_populates="todos")
    assignee = relationship("Member")


# ---------------- 假期 ----------------
class Holiday(Base):
    """成员假期"""
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    holiday_type = Column(String(16), default="personal")  # personal / sick / annual / public
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    note = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    member = relationship("Member", back_populates="holidays")
    project = relationship("Project")


# ---------------- 活动日志（可选扩展） ----------------
class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    actor = Column(String(64), nullable=True)
    action = Column(String(64), nullable=False)
    target = Column(String(128), nullable=True)
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ---------------- 种子数据 ----------------
def seed(db) -> None:
    """首次启动写入示例数据，便于直接体验"""
    if db.query(Member).count() == 0:
        colors = ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399", "#9254DE"]
        names = [("张伟", "PM"), ("李娜", "前端"), ("王强", "后端"), ("刘洋", "测试"), ("陈静", "设计")]
        for i, (n, r) in enumerate(names):
            db.add(Member(name=n, role=r, avatar_color=colors[i % len(colors)]))
        db.commit()
    if db.query(Project).count() == 0:
        p = Project(
            name="项目管理工具示例项目",
            code="DEMO",
            description="这是一个演示项目，包含了多层级任务、富文本需求、附件、甘特图、会议记录等所有功能。",
            status="active",
            priority="P1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            color="#409EFF",
        )
        db.add(p)
        db.commit()
        # 示例任务：1 个父 + 2 个子
        members = db.query(Member).all()
        from datetime import timedelta
        t0 = Task(
            project_id=p.id,
            title="需求分析与设计",
            content_html="<h3>需求分析</h3><p>梳理核心业务流程，输出 PRD 与原型。</p>",
            status="done",
            priority="P0",
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 20),
            planned_hours=40,
            actual_hours=38,
            progress=100,
            owner_id=members[0].id if members else None,
            sort_order=0,
        )
        db.add(t0)
        db.commit()
        for idx, (title, sd, ed, st, owner_idx) in enumerate([
            ("原型设计", date(2026, 1, 5), date(2026, 1, 12), "done", 4),
            ("PRD 文档", date(2026, 1, 10), date(2026, 1, 20), "done", 0),
        ]):
            db.add(Task(
                project_id=p.id, parent_id=t0.id, title=title,
                content_html=f"<p>{title}的详细描述</p>",
                status=st, priority="P1", start_date=sd, end_date=ed,
                planned_hours=24, actual_hours=20, progress=100,
                owner_id=members[owner_idx].id if members else None,
                sort_order=idx,
            ))
        # 进行中任务
        t1 = Task(
            project_id=p.id,
            title="开发实现",
            content_html="<h3>开发计划</h3><p>按模块拆分任务并行开发。</p>",
            status="doing",
            priority="P0",
            start_date=date(2026, 2, 1),
            end_date=date(2026, 4, 30),
            planned_hours=200,
            actual_hours=120,
            progress=50,
            owner_id=members[0].id if members else None,
            sort_order=1,
        )
        db.add(t1)
        db.commit()
        for idx, (title, sd, ed, owner_idx) in enumerate([
            ("后端 API 开发", date(2026, 2, 1), date(2026, 3, 15), 2),
            ("前端页面开发", date(2026, 2, 10), date(2026, 3, 30), 1),
            ("联调测试", date(2026, 3, 20), date(2026, 4, 30), 3),
        ]):
            db.add(Task(
                project_id=p.id, parent_id=t1.id, title=title,
                content_html=f"<p>{title}</p>",
                status="doing" if idx < 2 else "todo", priority="P1",
                start_date=sd, end_date=ed,
                planned_hours=80, actual_hours=40 if idx == 0 else 0,
                progress=60 if idx == 0 else (30 if idx == 1 else 0),
                owner_id=members[owner_idx].id if members else None,
                sort_order=idx,
            ))
        # 示例会议
        m = Meeting(
            project_id=p.id,
            title="周会 - 第 1 周",
            meeting_type="weekly",
            meeting_date=date(2026, 1, 8),
            start_time="10:00",
            end_time="11:00",
            host_id=members[0].id if members else None,
            attendees=[m.id for m in members],
            content_html="<p>讨论需求分析进度，确认设计稿。</p>",
        )
        db.add(m)
        db.commit()
        db.add(Todo(
            project_id=p.id, meeting_id=m.id,
            title="完成 PRD 评审",
            content="本周内组织 PRD 评审会议",
            assignee_id=members[0].id if members else None,
            mention_ids=[members[i].id for i in range(min(3, len(members)))] if members else [],
            status="done", priority="P0", due_date=date(2026, 1, 15),
        ))
        db.add(Todo(
            project_id=p.id, meeting_id=m.id,
            title="确认设计资源排期",
            content="@设计师 请安排资源",
            assignee_id=members[4].id if len(members) > 4 else None,
            mention_ids=[members[4].id] if len(members) > 4 else [],
            status="open", priority="P1", due_date=date(2026, 1, 12),
        ))
        db.commit()
