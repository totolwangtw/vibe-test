"""附件路由 - 文件上传/下载"""
import os
import time
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings, UPLOAD_DIR
from app.database import get_db
from app import models, schemas
from app.crud import get_or_404

router = APIRouter(prefix="/api", tags=["attachments"])


@router.post("/tasks/{tid}/attachments", response_model=schemas.AttachmentOut)
async def upload_attachment(tid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    get_or_404(db, models.Task, tid)
    if not file.filename:
        raise HTTPException(400, "文件名为空")
    # 防止文件名包含非法字符
    safe_name = os.path.basename(file.filename)
    stored_name = f"{int(time.time() * 1000)}_{safe_name}"
    target = Path(UPLOAD_DIR) / stored_name
    content = await file.read()
    target.write_bytes(content)
    att = models.Attachment(
        task_id=tid,
        filename=safe_name,
        stored_name=stored_name,
        size=len(content),
        mime_type=file.content_type or "application/octet-stream",
    )
    db.add(att)
    db.commit()
    db.refresh(att)
    return att


@router.get("/tasks/{tid}/attachments", response_model=list[schemas.AttachmentOut])
def list_attachments(tid: int, db: Session = Depends(get_db)):
    return db.query(models.Attachment).filter_by(task_id=tid).order_by(models.Attachment.uploaded_at.desc()).all()


@router.get("/attachments/{aid}/download")
def download_attachment(aid: int, db: Session = Depends(get_db)):
    att = get_or_404(db, models.Attachment, aid)
    fp = Path(UPLOAD_DIR) / att.stored_name
    if not fp.exists():
        raise HTTPException(404, "文件不存在")
    return FileResponse(str(fp), filename=att.filename, media_type=att.mime_type or "application/octet-stream")


@router.delete("/attachments/{aid}")
def delete_attachment(aid: int, db: Session = Depends(get_db)):
    att = get_or_404(db, models.Attachment, aid)
    fp = Path(UPLOAD_DIR) / att.stored_name
    if fp.exists():
        try:
            fp.unlink()
        except OSError:
            pass
    db.delete(att)
    db.commit()
    return {"ok": True}
