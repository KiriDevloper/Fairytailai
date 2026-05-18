from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, field_validator

from database.models      import User
from services.auth_service import (hash_password, verify_password,
                                    create_access_token, require_login,
                                    get_usage_info)
from utils.response_helper import success
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Schemas ───────────────────────────────────────────

class RegisterRequest(BaseModel):
    full_name:        str
    username:         str
    email:            EmailStr
    password:         str
    confirm_password: str
    agreed_terms:     bool
    agreed_privacy:   bool
    agreed_age:       bool

    @field_validator("username")
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("Ten tai khoan phai tu 3 ky tu")
        if not v.replace("_", "").isalnum():
            raise ValueError("Ten tai khoan chi duoc chua chu, so, va _")
        return v.lower()

    @field_validator("password")
    def password_strong(cls, v):
        if len(v) < 6:
            raise ValueError("Mat khau phai tu 6 ky tu")
        return v


class LoginRequest(BaseModel):
    username_or_email: str
    password:          str
    remember_me:       bool = False


# ── REGISTER ──────────────────────────────────────────

@router.post("/register")
async def register(req: RegisterRequest):
    if not (req.agreed_terms and req.agreed_privacy and req.agreed_age):
        raise HTTPException(400, "Vui long dong y tat ca dieu khoan de dang ky")
    if req.password != req.confirm_password:
        raise HTTPException(400, "Mat khau xac nhan khong khop")
    if await User.find_one(User.username == req.username.lower()):
        raise HTTPException(400, "Ten tai khoan da duoc su dung")
    if await User.find_one(User.email == req.email.lower()):
        raise HTTPException(400, "Email nay da duoc dang ky")

    user = User(
        full_name       = req.full_name.strip(),
        username        = req.username.lower(),
        email           = req.email.lower(),
        hashed_password = hash_password(req.password),
        agreed_terms    = True,
        agreed_privacy  = True,
        agreed_age      = True,
    )
    await user.insert()
    token = create_access_token(str(user.id))

    return success({
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":        str(user.id),
            "full_name": user.full_name,
            "username":  user.username,
            "email":     user.email,
            "plan":      user.plan,
        }
    }, message=f"Dang ky thanh cong! Chao mung {user.full_name}!")


# ── LOGIN ─────────────────────────────────────────────
# Đường dẫn mà Swagger sẽ dùng để lấy Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/swagger-login")

# Endpoint dành riêng cho nút Authorize của Swagger
@router.post("/swagger-login", include_in_schema=False) # Ẩn khỏi danh sách API
async def swagger_login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Gọi lại chính logic login của bạn hoặc viết gọn ở đây
    ident = form_data.username.strip().lower()
    user = (await User.find_one(User.username == ident) or 
            await User.find_one(User.email == ident))
            
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Sai tài khoản hoặc mật khẩu")
        
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}
@router.post("/login")
async def login(req: LoginRequest):
    ident = req.username_or_email.strip().lower()
    user  = (await User.find_one(User.username == ident) or
             await User.find_one(User.email    == ident))

    if not user:
        raise HTTPException(400, "Tai khoan khong ton tai")
    if not verify_password(req.password, user.hashed_password or ""):
        raise HTTPException(400, "Mat khau khong chinh xac")
    if not user.is_active:
        raise HTTPException(400, "Tai khoan da bi khoa")

    token = create_access_token(str(user.id))
    usage = await get_usage_info(user)

    return success({
        "access_token": token,
        "token_type":   "bearer",
        "remember_me":  req.remember_me,
        "user": {
            "id":        str(user.id),
            "full_name": user.full_name,
            "username":  user.username,
            "email":     user.email,
            "plan":      user.plan,
        },
        "usage": usage,
    }, message=f"Xin chao, {user.full_name}!")


# ── ME ────────────────────────────────────────────────

@router.get("/me")
async def get_me(user: User = Depends(require_login)):
    usage = await get_usage_info(user)
    return success({
        "id":         str(user.id),
        "full_name":  user.full_name,
        "username":   user.username,
        "email":      user.email,
        "plan":       user.plan,
        "usage":      usage,
        "created_at": user.created_at.isoformat(),
    })


@router.post("/logout")
async def logout():
    return success(None, message="Da dang xuat. Hen gap lai!")