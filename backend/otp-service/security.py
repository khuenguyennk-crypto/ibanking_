import os

from fastapi import Header, HTTPException

INTERNAL_KEY = os.getenv("INTERNAL_KEY", "dev-internal-key")


def verify_internal_key(x_internal_key: str = Header(default=None)) -> None:
    if x_internal_key != INTERNAL_KEY:
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_INTERNAL_KEY", "message": "Khóa không hợp lệ"},
        )
        