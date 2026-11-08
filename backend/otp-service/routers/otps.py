import os
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from db import get_db
from mailer import MailError, send_otp_email
from models import Otp
from schemas import OtpCreateRequest, OtpCreated, OtpVerified, OtpVerifyRequest
from security import verify_internal_key

router = APIRouter(tags=["OTP"], dependencies=[Depends(verify_internal_key)])

OTP_VALID_SECONDS = int(os.environ["OTP_VALID_SECONDS"])


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _latest_otp(db: Session, transaction_id: int):
    return (
        db.query(Otp)
        .filter(Otp.transaction_id == transaction_id)
        .order_by(Otp.otp_id.desc())
        .first()
    )


def _generate_unique_code(db: Session, now: datetime) -> str:
    active = {
        code
        for (code,) in db.query(Otp.otp_code)
        .filter(Otp.is_used.is_(False), Otp.expires_at > now)
        .all()
    }
    for _ in range(20):
        code = f"{secrets.randbelow(1_000_000):06d}"
        if code not in active:
            return code
    raise HTTPException(
        status_code=503,
        detail={"code": "OTP_GENERATION_FAILED", "message": "Không tạo được mã OTP, vui lòng thử lại"},
    )


@router.post("/internal/otps", response_model=OtpCreated, status_code=201)
def create_otp(body: OtpCreateRequest, db: Session = Depends(get_db)):
    now = _now()
    code = _generate_unique_code(db, now)
    otp = Otp(
        transaction_id=body.transaction_id,
        otp_code=code,
        created_at=now,
        expires_at=now + timedelta(seconds=OTP_VALID_SECONDS),
        is_used=False,
    )
    db.add(otp)
    db.commit()

    try:
        send_otp_email(body.email, body.full_name, code, OTP_VALID_SECONDS // 60)
    except MailError:
        otp.is_used = True
        db.commit()
        raise HTTPException(
            status_code=502,
            detail={"code": "EMAIL_SEND_FAILED", "message": "Không gửi được email OTP"},
        )

    return {
        "transaction_id": body.transaction_id,
        "expires_at": otp.expires_at,
        "expires_in": OTP_VALID_SECONDS,
    }


@router.post("/internal/otps/verify", response_model=OtpVerified)
def verify_otp(body: OtpVerifyRequest, db: Session = Depends(get_db)):
    now = _now()

    latest = _latest_otp(db, body.transaction_id)
    if latest is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "OTP_NOT_FOUND", "message": "Giao dịch này chưa có mã OTP"},
        )

    result = db.execute(
        update(Otp)
        .where(
            Otp.otp_id == latest.otp_id,
            Otp.otp_code == body.otp_code,
            Otp.is_used.is_(False),
            Otp.expires_at > now,
        )
        .values(is_used=True)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 1:
        db.commit()
        return {"transaction_id": body.transaction_id, "valid": True}

    db.rollback()
    latest = _latest_otp(db, body.transaction_id)

    if latest.otp_code == body.otp_code and latest.is_used:
        raise HTTPException(
            status_code=409,
            detail={"code": "OTP_ALREADY_USED", "message": "Mã OTP đã được sử dụng"},
        )
    if latest.expires_at <= now:
        raise HTTPException(
            status_code=400,
            detail={"code": "OTP_EXPIRED", "message": "Mã OTP đã hết hạn"},
        )
    raise HTTPException(
        status_code=400,
        detail={"code": "OTP_INVALID", "message": "Mã OTP không đúng"},
    )
    