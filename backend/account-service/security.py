import os

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALGORITHM = "HS256"
INTERNAL_KEY = os.getenv("INTERNAL_KEY", "dev-internal-key")

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> int:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHORIZED", "message": "Chưa đăng nhập"},
        )
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_TOKEN", "message": "Phiên đăng nhập không hợp lệ hoặc đã hết hạn"},
        )


def verify_internal_key(x_internal_key: str = Header(default=None)) -> None:
    if x_internal_key != INTERNAL_KEY:
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_INTERNAL_KEY", "message": "Khóa không hợp lệ"},
        )
        