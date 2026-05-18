from beanie import Document, Indexed
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum


class StatusEnum(str, Enum):
    PENDING = "pending"
    DONE    = "done"
    FAILED  = "failed"


class PlanEnum(str, Enum):
    FREE    = "free"
    PREMIUM = "premium"


class UsageLog(BaseModel):
    used_at:  datetime = Field(default_factory=datetime.utcnow)
    story_id: Optional[str] = None


class User(Document):
    full_name:       str
    username:        Indexed(str, unique=True)
    email:           Indexed(str, unique=True)
    hashed_password: str

    plan:        PlanEnum      = PlanEnum.FREE
    usage_today: int           = 0
    usage_date:  Optional[date] = None
    usage_logs:  List[UsageLog] = []

    agreed_terms:   bool = False
    agreed_privacy: bool = False
    agreed_age:     bool = False

    is_active:  bool     = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

    @property
    def is_premium(self) -> bool:
        return self.plan == PlanEnum.PREMIUM


class FilePaths(BaseModel):
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    video_path: Optional[str] = None


class Story(Document):
    user_id:       Optional[str] = None
    title:         Optional[str] = None
    user_text:     str
    script:        Optional[str] = None
    files:         FilePaths     = Field(default_factory=FilePaths)
    status:        StatusEnum    = StatusEnum.PENDING
    error_message: Optional[str] = None
    session_id:    str           = ""
    created_at:    datetime      = Field(default_factory=datetime.utcnow)
    updated_at:    datetime      = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "stories"