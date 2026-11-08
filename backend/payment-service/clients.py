import logging
import os
import time
from decimal import Decimal

import httpx

logger = logging.getLogger("clients")

USER_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
ACCOUNT_URL = os.getenv("ACCOUNT_SERVICE_URL", "http://account-service:8000")
TUITION_URL = os.getenv("TUITION_SERVICE_URL", "http://tuition-service:8000")
OTP_URL = os.getenv("OTP_SERVICE_URL", "http://otp-service:8000")

INTERNAL_KEY = os.getenv("INTERNAL_KEY", "dev-internal-key")
MAX_ATTEMPTS = 3

_client = httpx.Client(headers={"X-Internal-Key": INTERNAL_KEY})


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(f"{status} {code}: {message}")
        self.status = status
        self.code = code
        self.message = message


class ServiceUnavailable(Exception):
    pass


def _to_error(response: httpx.Response) -> ServiceError:
    code, message = "SERVICE_ERROR", "Lỗi từ service nội bộ"
    try:
        err = response.json().get("error", {})
        code = err.get("code", code)
        message = err.get("message", message)
    except ValueError:
        pass
    return ServiceError(response.status_code, code, message)


def _call(method: str, url: str, *, json=None, params=None, timeout: float = 5.0, attempts: int = MAX_ATTEMPTS):
    last = ""
    for attempt in range(1, attempts + 1):
        try:
            response = _client.request(method, url, json=json, params=params, timeout=timeout)
        except httpx.HTTPError as exc:
            last = repr(exc)
        else:
            if response.status_code >= 500:
                last = f"HTTP {response.status_code}"
            elif response.status_code >= 400:
                raise _to_error(response)
            else:
                return response.json()
        if attempt < attempts:
            time.sleep(0.3 * attempt)
    logger.error("Gọi %s %s thất bại sau %d lần: %s", method, url, attempts, last)
    raise ServiceUnavailable(f"{method} {url}: {last}")


def get_user(user_id: int) -> dict:
    return _call("GET", f"{USER_URL}/internal/users/{user_id}")


def get_account(account_id: int) -> dict:
    return _call("GET", f"{ACCOUNT_URL}/internal/accounts/{account_id}")


def list_accounts(user_id: int) -> list:
    return _call("GET", f"{ACCOUNT_URL}/internal/accounts", params={"user_id": user_id})


def debit(account_id: int, transaction_id: int, amount: Decimal) -> dict:
    return _call(
        "POST",
        f"{ACCOUNT_URL}/internal/accounts/{account_id}/debit",
        json={"transaction_id": transaction_id, "amount": str(amount)},
    )


def refund(account_id: int, transaction_id: int) -> dict:
    return _call(
        "POST",
        f"{ACCOUNT_URL}/internal/accounts/{account_id}/refund",
        json={"transaction_id": transaction_id},
    )


def get_tuition(tuition_id: int, attempts: int = MAX_ATTEMPTS) -> dict:
    return _call("GET", f"{TUITION_URL}/internal/tuitions/{tuition_id}", attempts=attempts)


def pay_tuition(tuition_id: int, transaction_id: int, amount: Decimal) -> dict:
    return _call(
        "POST",
        f"{TUITION_URL}/internal/tuitions/{tuition_id}/pay",
        json={"transaction_id": transaction_id, "amount": str(amount)},
    )


def create_otp(transaction_id: int, email: str, full_name: str) -> dict:
    return _call(
        "POST",
        f"{OTP_URL}/internal/otps",
        json={"transaction_id": transaction_id, "email": email, "full_name": full_name},
        timeout=20.0,
        attempts=1,
    )


def verify_otp(transaction_id: int, otp_code: str) -> dict:
    return _call(
        "POST",
        f"{OTP_URL}/internal/otps/verify",
        json={"transaction_id": transaction_id, "otp_code": otp_code},
        attempts=1,
    )


def notify_success(payload: dict) -> dict:
    return _call("POST", f"{OTP_URL}/internal/notifications/payment-success", json=payload, attempts=1)
