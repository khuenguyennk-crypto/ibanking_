import logging
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import update
from sqlalchemy.orm import Session

import clients
from models import Transaction

logger = logging.getLogger("saga")

OTP_VALID_SECONDS = int(os.environ["OTP_VALID_SECONDS"])
STUCK_AFTER_SECONDS = int(os.getenv("STUCK_AFTER_SECONDS") or 60)


def now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def transition(db: Session, tx_id: int, from_statuses: list, **values) -> bool:
    values["updated_at"] = now_utc()
    result = db.execute(
        update(Transaction)
        .where(Transaction.transaction_id == tx_id, Transaction.status.in_(from_statuses))
        .values(**values)
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return result.rowcount == 1


def _finish(db: Session, tx_id: int, status: str, reason: str | None = None) -> bool:
    return transition(
        db,
        tx_id,
        ["processing"],
        status=status,
        completed_at=now_utc(),
        failure_reason=(reason[:255] if reason else None),
    )


def _status_of(db: Session, tx_id: int) -> str:
    return db.query(Transaction.status).filter(Transaction.transaction_id == tx_id).scalar()


def _notify_success(account_id: int, tuition_id: int, tx_id: int, amount: Decimal) -> None:
    try:
        account = clients.get_account(account_id)
        user = clients.get_user(account["user_id"])
        tuition = clients.get_tuition(tuition_id)
        clients.notify_success(
            {
                "transaction_id": tx_id,
                "email": user["email"],
                "full_name": user["full_name"],
                "student_id": tuition["student_id"],
                "student_name": tuition["student_name"],
                "semester": tuition["semester"],
                "amount": str(amount),
            }
        )
    except (clients.ServiceError, clients.ServiceUnavailable) as exc:
        logger.warning("Không gửi được email xác nhận cho giao dịch %s: %s", tx_id, exc)


def _refund_and_fail(db: Session, tx_id: int, account_id: int, reason: str) -> str:
    try:
        clients.refund(account_id, tx_id)
    except clients.ServiceError as exc:
        if exc.code != "DEBIT_NOT_FOUND":
            logger.error("Hoàn tiền giao dịch %s bị từ chối (%s) - CẦN KIỂM TRA THỦ CÔNG", tx_id, exc)
            return "processing"
    except clients.ServiceUnavailable:
        return "processing"

    _finish(db, tx_id, "failed", reason)
    return _status_of(db, tx_id)


def run_saga(db: Session, tx_id: int) -> str:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        return "missing"
    if tx.status != "processing":
        return tx.status
    account_id, tuition_id, amount = tx.bank_account_id, tx.tuition_id, tx.amount
    db.rollback()

    try:
        clients.debit(account_id, tx_id, amount)
    except clients.ServiceError as exc:
        _finish(db, tx_id, "failed", exc.message)
        return _status_of(db, tx_id)
    except clients.ServiceUnavailable:
        return "processing"

    try:
        clients.pay_tuition(tuition_id, tx_id, amount)
    except clients.ServiceError as exc:
        return _refund_and_fail(db, tx_id, account_id, exc.message)
    except clients.ServiceUnavailable:
        return "processing"
    if _finish(db, tx_id, "success"):
        _notify_success(account_id, tuition_id, tx_id, amount)
    return _status_of(db, tx_id)


def expire_stale(db: Session) -> int:
    now = now_utc()
    cutoff = now - timedelta(seconds=OTP_VALID_SECONDS)
    result = db.execute(
        update(Transaction)
        .where(Transaction.status.in_(["pending", "otp_sent"]), Transaction.updated_at < cutoff)
        .values(
            status="expired",
            failure_reason="OTP hết hạn, giao dịch đã bị hủy",
            completed_at=now,
            updated_at=now,
        )
        .execution_options(synchronize_session=False)
    )
    db.commit()
    return result.rowcount


def recover_stuck(db: Session) -> int:
    cutoff = now_utc() - timedelta(seconds=STUCK_AFTER_SECONDS)
    ids = [
        tx_id
        for (tx_id,) in db.query(Transaction.transaction_id)
        .filter(Transaction.status == "processing", Transaction.updated_at < cutoff)
        .all()
    ]
    db.rollback()
    for tx_id in ids:
        if run_saga(db, tx_id) == "processing":
            transition(db, tx_id, ["processing"])
    return len(ids)
