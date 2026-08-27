"""数据库连接与会话管理"""
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# SQLite 需要 check_same_thread=False 才能在 FastAPI 多线程下使用
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """建表 + 写入种子数据"""
    from app import models  # noqa: F401  保证模型被加载
    Base.metadata.create_all(bind=engine)
    models.seed(db=SessionLocal())
