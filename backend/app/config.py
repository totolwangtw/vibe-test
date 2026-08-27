"""项目管理工具 - 后端配置"""
from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent  # /workspace
BACKEND_DIR = Path(__file__).resolve().parent.parent       # /workspace/backend
DATA_DIR = BACKEND_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
STATIC_DIR = BASE_DIR / "frontend" / "dist"

for _d in (DATA_DIR, UPLOAD_DIR):
    _d.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    app_name: str = "项目管理工具"
    version: str = "1.0.0"
    # SQLite 数据库文件（放于 backend/data/ 下，整个文件夹复制到 Windows 即可用）
    database_url: str = f"sqlite:///{(DATA_DIR / 'pm.db').as_posix()}"
    # 上传文件目录
    upload_dir: str = str(UPLOAD_DIR)
    # 前端构建产物目录（生产环境由 FastAPI 托管）
    static_dir: str = str(STATIC_DIR)
    # CORS（开发态前端跑在 5173 端口）
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # 监听
    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()
