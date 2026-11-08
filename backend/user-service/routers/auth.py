from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models import User
from schemas import LoginRequest, LoginResponse
from security import (
    JWT_EXPIRE_SECONDS,
    create_access_token,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["Đăng nhập"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == body.username).first()

    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "message": "Sai username hoặc mật khẩu"},
        )

    token = create_access_token(user.user_id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": JWT_EXPIRE_SECONDS,
        "user": {"user_id": user.user_id, "full_name": user.full_name},
    }
    