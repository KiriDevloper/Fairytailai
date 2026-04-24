from beanie import Document, Indexed
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class StatusEnum(str, Enum):
    PENDING = "pending"
    DONE    = "done"
    FAILED  = "failed"


class FilePaths(BaseModel):
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    video_path: Optional[str] = None


class Story(Document):
    # Noi dung cau chuyen
    title:    Optional[str] = None
    user_text: str
    script:   Optional[str] = None

    # File dinh kem
    files: FilePaths = Field(default_factory=FilePaths)

    # Trang thai xu ly
    status:        StatusEnum       = StatusEnum.PENDING
    error_message: Optional[str]    = None

    # Phien lam viec
    session_id: Indexed(str) = ""

    # Thoi gian
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "stories"