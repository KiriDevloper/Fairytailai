import os
from datetime import datetime, timedelta, date, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from database.models import User, PlanEnum, UsageLog

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fairytale-secret-2025")
ALGORITHM  = "HS256"
TOKEN_EXPIRE_DAYS = 7

FREE_LIMIT    = 1
HARD_CAP      = 3
PREMIUM_LIMIT = 999

pwd_context   = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/swagger-login")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expire  = datetime.now(timezone.utc) + timedelta(days=TOKEN_EXPIRE_DAYS)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("sub")
        if not uid:
            return None
        return await User.get(uid)
    except JWTError:
        return None


async def require_login(token: str = Depends(oauth2_scheme)) -> User:
    user = await get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chua dang nhap",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def check_and_consume(user: User, story_id: str = None) -> dict:
    today = date.today()
    if user.usage_date != today:
        user.usage_today = 0
        user.usage_date  = today

    limit = FREE_LIMIT if not user.is_premium else PREMIUM_LIMIT
    used  = user.usage_today

    # Qua gioi han cung (3 luot) -> bat buoc mua
    if used >= HARD_CAP and not user.is_premium:
        return {
            "allowed":      False,
            "used_today":   used,
            "limit":        limit,
            "remaining":    0,
            "need_upgrade": True,
            "message":      f"Ban da dung {HARD_CAP} luot hom nay. Mua Premium de dung khong gioi han!"
        }

    # Het luot free (1 luot) nhung chua qua hard cap
    if used >= limit and not user.is_premium:
        return {
            "allowed":      False,
            "used_today":   used,
            "limit":        limit,
            "remaining":    0,
            "need_upgrade": False,
            "message":      f"Ban da het {limit} luot mien phi hom nay. Quay lai ngay mai hoac mua Premium!"
        }

    # Con luot -> tru luot
    user.usage_today += 1
    user.usage_logs.append(UsageLog(used_at=datetime.utcnow(), story_id=story_id))
    user.updated_at = datetime.utcnow()
    await user.save()

    return {
        "allowed":      True,
        "used_today":   user.usage_today,
        "limit":        limit,
        "remaining":    max(0, limit - user.usage_today),
        "need_upgrade": False,
        "message":      "OK"
    }


async def get_usage_info(user: User) -> dict:
    today = date.today()
    used  = user.usage_today if user.usage_date == today else 0
    limit = FREE_LIMIT if not user.is_premium else PREMIUM_LIMIT
    return {
        "used_today":    used,
        "limit":         limit,
        "hard_cap":      HARD_CAP,
        "remaining":     max(0, limit - used),
        "is_premium":    user.is_premium,
        "plan":          user.plan,
        "usage_history": [
            {"used_at": log.used_at.isoformat(), "story_id": log.story_id}
            for log in (user.usage_logs or [])[-10:]
        ]
    }