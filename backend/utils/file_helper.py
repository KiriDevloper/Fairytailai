import os
import uuid
from fastapi import UploadFile
from config import UPLOAD_DIR


def generate_id() -> str:
    """Tao ID doc nhat cho moi story."""
    return uuid.uuid4().hex


async def save_upload(file: UploadFile, story_id: str) -> str:
    """Luu file upload vao thu muc uploads/, tra ve duong dan."""
    ext        = os.path.splitext(file.filename)[-1] or ".jpg"
    image_path = os.path.join(UPLOAD_DIR, f"{story_id}{ext}")
    content    = await file.read()
    with open(image_path, "wb") as f:
        f.write(content)
    return image_path


def build_output_path(story_id: str, ext: str) -> str:
    """Tao duong dan file output (audio/video)."""
    from config import OUTPUT_DIR
    return os.path.join(OUTPUT_DIR, f"{story_id}{ext}")


def file_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) > 0