"""
工具函数
"""

import os
import uuid
from PIL import Image as PilImage
from dotenv import load_dotenv

load_dotenv()

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads/originals")
THUMB_DIR = os.getenv("THUMB_DIR", "uploads/thumbnails")
MAX_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 10))
THUMB_SIZE = (300, 300)

def allowed_file_size(file_size: int) -> bool:
    return file_size <= MAX_SIZE_MB * 1024 * 1024

def generate_filename(original_name: str) -> str:
    ext = original_name.rsplit(".", 1)[-1] if "." in original_name else "png"
    return f"{uuid.uuid4().hex}.{ext}"

def save_image(file_data, filename: str) -> str:
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(file_data)
    return file_path

def create_thumbnail(original_path: str, thumb_filename: str):
    thumb_path = os.path.join(THUMB_DIR, thumb_filename)
    with PilImage.open(original_path) as img:
        img.thumbnail(THUMB_SIZE)
        img.save(thumb_path)
    return thumb_path