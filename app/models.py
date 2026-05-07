"""
数据模型
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)      # 随机文件名
    original_name = Column(String)                          # 原始文件名
    size = Column(Integer)                                  # 字节数
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    access_count = Column(Integer, default=0)
