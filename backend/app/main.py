"""FastAPI 主应用"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings, STATIC_DIR
from app.database import init_db
from app.routers import (
    attachments,
    changes,
    csv as csv_router,
    dashboard,
    holidays,
    issues,
    meetings,
    members,
    projects,
    risks,
    tasks,
    todos,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表 + 写入种子数据
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    lifespan=lifespan,
    description="本地项目管理工具 - FastAPI + SQLite + Vue(Vben 风格)",
)

# CORS（开发态前端跑在 5173）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["*"],  # 本地工具，全开
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
for r in (members, projects, tasks, attachments, meetings, todos, holidays,
          dashboard, changes, risks, issues, csv_router):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name, "version": settings.version}


@app.get("/api/config")
def app_config():
    return {
        "priority_options": ["P0", "P1", "P2", "P3"],
        "status_options": ["todo", "doing", "done", "blocked"],
        "meeting_types": ["daily", "weekly"],
        "todo_status": ["open", "in_progress", "done"],
        "holiday_types": ["personal", "sick", "annual", "public"],
        "task_types": ["task", "milestone", "bug", "story"],
    }


# 生产模式：托管前端 dist
if Path(STATIC_DIR).exists() and (Path(STATIC_DIR) / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=Path(STATIC_DIR) / "assets"), name="assets")

    @app.get("/")
    def root_index():
        return FileResponse(Path(STATIC_DIR) / "index.html")

    # SPA 回退：非 /api/* 路径回退到 index.html
    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        if full_path.startswith("api"):
            return {"detail": "Not Found"}
        candidate = Path(STATIC_DIR) / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(Path(STATIC_DIR) / "index.html")
else:
    @app.get("/")
    def root_index():
        return {
            "message": "前端尚未构建。开发模式下请 cd frontend && pnpm dev。",
            "frontend_dist": str(STATIC_DIR),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        # 反向代理后启用：信任 X-Forwarded-* 头，获取真实客户端 IP / 协议
        proxy_headers=settings.proxy_headers,
        forwarded_allow_ips=settings.forwarded_allow_ips,
    )
