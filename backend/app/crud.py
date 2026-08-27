"""通用 CRUD 辅助函数"""
from typing import Any, Type, TypeVar
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def get_or_404(db: Session, model: Type[ModelT], id_: int) -> ModelT:
    obj = db.get(model, id_)
    if obj is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"{model.__name__} {id_} not found")
    return obj


def apply_update(db_obj: Any, schema: BaseModel) -> None:
    """将 schema 中非 None 的字段写入 db_obj"""
    data = schema.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_obj, k, v)
