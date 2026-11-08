import os

import httpx
from fastapi import HTTPException

USER_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
INTERNAL_KEY = os.getenv("INTERNAL_KEY", "dev-internal-key")


def verify_password(user_id: int, password: str) -> bool:
    try:
        response = httpx.post(
            f"{USER_URL}/internal/users/{user_id}/verify-password",
            json={"password": password},
            headers={"X-Internal-Key": INTERNAL_KEY},
            timeout=5,
        )
        response.raise_for_status()
        return bool(response.json().get("valid"))
    except httpx.HTTPError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "USER_SERVICE_UNAVAILABLE",
                "message": "Chưa xác minh được mật khẩu, vui lòng thử lại sau",
            },
        )
        