"""
CRUD 操作
"""

from sqlalchemy.orm import Session
from app import models
import os
from dotenv import load_dotenv

load_dotenv()
THUMB_DIR = os.getenv("THUMB_DIR", "uploads/thumbnails")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/originals")


def create_image(db: Session, filename: str, original_name: str, size: int):
    db_image = models.Image(
        filename=filename,
        original_name=original_name,
        size=size
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def get_images(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Image).order_by(models.Image.upload_time.desc()).offset(skip).limit(limit).all()


def get_image_by_filename(db: Session, filename: str):
    return db.query(models.Image).filter(models.Image.filename == filename).first()


# def delete_image(db: Session, image_id: int):
#     db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
#     if db_image:
#         # 删除原图和缩略图
#         original_path = os.path.join(UPLOAD_DIR, db_image.filename)
#         thumb_path = os.path.join(THUMB_DIR, db_image.filename)
#         if os.path.exists(original_path):
#             os.remove(original_path)
#         if os.path.exists(thumb_path):
#             os.remove(thumb_path)
#         db.delete(db_image)
#         db.commit()
#     return db_image

def delete_image(db: Session, image_id: int):
    db_image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if db_image:
        # 安全删除原图（如果存在）
        original_path = os.path.join(UPLOAD_DIR, db_image.filename)
        if os.path.exists(original_path):
            os.remove(original_path)
        # 安全删除缩略图（如果存在）
        thumb_path = os.path.join(THUMB_DIR, db_image.filename)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        db.delete(db_image)
        db.commit()
    return db_image
