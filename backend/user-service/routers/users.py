from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from db import get_db
from models import User
from schemas import UserInternal, UserMe
from security import get_current_user_id, verify_internal_key, verify_password

router = APIRouter(tags=["Người dùng"])


class VerifyPasswordRequest(BaseModel):
    password: str = Field(min_length=1)


def _user_not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "USER_NOT_FOUND", "message": "Không tìm thấy người dùng"},
    )


@router.get("/api/users/me", response_model=UserMe)
def get_me(user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise _user_not_found()
    return user


@router.get(
    "/internal/users/{user_id}",
    response_model=UserInternal,
    dependencies=[Depends(verify_internal_key)],
)
def get_user_internal(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if user is None:
        raise _user_not_found()
    return user


@router.post(
    "/internal/users/{user_id}/verify-password",
    dependencies=[Depends(verify_internal_key)],
)
def verify_user_password(
    user_id: int,
    body: VerifyPasswordRequest,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise _user_not_found()
    return {"valid": verify_password(body.password, user.password_hash)}
