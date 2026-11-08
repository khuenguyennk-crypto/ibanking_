from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

import clients
import saga
from db import get_db
from models import Transaction
from schemas import (
    ConfirmRequest,
    CreatePaymentRequest,
    CreatePaymentResponse,
    HistoryItem,
    ResendOtpResponse,
    TransactionResponse,
)
from security import get_current_user_id

router = APIRouter(prefix="/api/payments", tags=["Thanh toán"])


def _raise_service_error(exc: clients.ServiceError):
    status = exc.status if exc.status in (400, 404, 409) else 502
    raise HTTPException(status_code=status, detail={"code": exc.code, "message": exc.message})


def _tx_not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "TRANSACTION_NOT_FOUND", "message": "Không tìm thấy giao dịch"},
    )


def _get_owned_transaction(db: Session, transaction_id: int, user_id: int) -> Transaction:
    tx = db.get(Transaction, transaction_id)
    if tx is None:
        raise _tx_not_found()
    try:
        account = clients.get_account(tx.bank_account_id)
    except clients.ServiceError as exc:
        _raise_service_error(exc)
    if account["user_id"] != user_id:
        raise _tx_not_found()
    return tx


@router.post("", response_model=CreatePaymentResponse, status_code=201)
def create_payment(
    body: CreatePaymentRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    try:
        account = clients.get_account(body.bank_account_id)
    except clients.ServiceError as exc:
        _raise_service_error(exc)
    if account["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail={"code": "ACCOUNT_NOT_OWNED", "message": "Tài khoản không thuộc về bạn"},
        )

    try:
        tuition = clients.get_tuition(body.tuition_id)
    except clients.ServiceError as exc:
        _raise_service_error(exc)
    if tuition["status"] != "unpaid":
        raise HTTPException(
            status_code=409,
            detail={"code": "TUITION_ALREADY_PAID", "message": "Khoản học phí này đã được thanh toán"},
        )

    amount = Decimal(str(tuition["amount"]))
    if Decimal(str(account["balance"])) < amount:
        raise HTTPException(
            status_code=409,
            detail={"code": "INSUFFICIENT_BALANCE", "message": "Số dư không đủ để thanh toán"},
        )

    try:
        user = clients.get_user(user_id)
    except clients.ServiceError as exc:
        _raise_service_error(exc)

    now = saga.now_utc()
    tx = Transaction(
        bank_account_id=body.bank_account_id,
        tuition_id=body.tuition_id,
        amount=amount,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    tx_id = tx.transaction_id

    try:
        clients.create_otp(tx_id, user["email"], user["full_name"])
    except (clients.ServiceError, clients.ServiceUnavailable):
        saga.transition(
            db, tx_id, ["pending"],
            status="failed", completed_at=saga.now_utc(), failure_reason="Không gửi được mã OTP",
        )
        raise HTTPException(
            status_code=502,
            detail={"code": "OTP_SEND_FAILED", "message": "Không gửi được mã OTP, vui lòng thử lại"},
        )
    saga.transition(db, tx_id, ["pending"], status="otp_sent")

    return {
        "transaction_id": tx_id,
        "status": "otp_sent",
        "amount": amount,
        "otp_expires_in": saga.OTP_VALID_SECONDS,
    }


@router.post("/{transaction_id}/confirm", response_model=TransactionResponse)
def confirm_payment(
    transaction_id: int,
    body: ConfirmRequest,
    response: Response,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    tx = _get_owned_transaction(db, transaction_id, user_id)

    if tx.status == "success":
        return tx
    if tx.status == "processing":
        response.status_code = 202
        return tx
    if tx.status in ("failed", "expired", "cancelled"):
        raise HTTPException(
            status_code=409,
            detail={"code": "TRANSACTION_CLOSED", "message": tx.failure_reason or "Giao dịch đã kết thúc",},
        )
    if tx.status == "pending":
        raise HTTPException(
            status_code=409,
            detail={"code": "TRANSACTION_NOT_READY", "message": "Giao dịch chưa gửi OTP"},
        )

    try:
        clients.verify_otp(transaction_id, body.otp_code)
    except clients.ServiceError as exc:
        if exc.code == "OTP_EXPIRED":
            saga.transition(
                db, transaction_id, ["otp_sent"],
                status="expired", completed_at=saga.now_utc(), failure_reason="OTP hết hạn, giao dịch đã bị hủy",
            )
        _raise_service_error(exc)

    if not saga.transition(db, transaction_id, ["otp_sent"], status="processing"):
        db.refresh(tx)
        if tx.status == "success":
            return tx
        response.status_code = 202
        return tx

    saga.run_saga(db, transaction_id)

    db.refresh(tx)
    if tx.status == "processing":
        response.status_code = 202
    return tx


@router.post("/{transaction_id}/resend-otp", response_model=ResendOtpResponse)
def resend_otp(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    tx = _get_owned_transaction(db, transaction_id, user_id)

    if tx.status != "otp_sent":
        raise HTTPException(
            status_code=409,
            detail={"code": "TRANSACTION_NOT_WAITING_OTP", "message": "Giao dịch không còn đợi OTP"},
        )
    if tx.updated_at + saga.timedelta(seconds=saga.OTP_VALID_SECONDS) <= saga.now_utc():
        saga.transition(
            db, transaction_id, ["otp_sent"],
            status="expired", completed_at=saga.now_utc(), failure_reason="OTP hết hạn, giao dịch đã bị hủy",
        )
        raise HTTPException(
            status_code=409,
            detail={"code": "TRANSACTION_EXPIRED", "message": "OTP đã hết hạn, vui lòng tạo giao dịch mới"},
        )

    try:
        user = clients.get_user(user_id)
        clients.create_otp(transaction_id, user["email"], user["full_name"])
    except clients.ServiceError as exc:
        _raise_service_error(exc)
    except clients.ServiceUnavailable:
        raise HTTPException(
            status_code=502,
            detail={"code": "OTP_SEND_FAILED", "message": "Không gửi được mã OTP, vui lòng thử lại"},
        )

    saga.transition(db, transaction_id, ["otp_sent"])
    return {
        "transaction_id": transaction_id,
        "status": "otp_sent",
        "otp_expires_in": saga.OTP_VALID_SECONDS,
    }


@router.post("/{transaction_id}/cancel", response_model=TransactionResponse)
def cancel_payment(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    tx = _get_owned_transaction(db, transaction_id, user_id)

    if saga.transition(
        db, transaction_id, ["pending", "otp_sent"],
        status="cancelled", completed_at=saga.now_utc(), failure_reason="Bạn đã hủy giao dịch",
    ):
        db.refresh(tx)
        return tx

    db.refresh(tx)
    if tx.status == "cancelled":
        return tx
    raise HTTPException(
        status_code=409,
        detail={"code": "TRANSACTION_NOT_CANCELLABLE", "message": "Giao dịch không thể hủy ở trạng thái hiện tại",},
    )
    

@router.get("", response_model=list[HistoryItem])
def history(
    limit: int = Query(default=50, ge=1, le=100),
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    accounts = clients.list_accounts(user_id)
    account_map = {a["bank_account_id"]: a for a in accounts}
    if not account_map:
        return []

    txs = (
        db.query(Transaction)
        .filter(Transaction.bank_account_id.in_(list(account_map)))
        .order_by(Transaction.transaction_id.desc())
        .limit(limit)
        .all()
    )

    tuition_cache: dict = {}
    tuition_service_down = False
    items = []
    for tx in txs:
        if tx.tuition_id not in tuition_cache and not tuition_service_down:
            try:
                tuition_cache[tx.tuition_id] = clients.get_tuition(tx.tuition_id, attempts=1)
            except clients.ServiceError:
                tuition_cache[tx.tuition_id] = None
            except clients.ServiceUnavailable:
                tuition_service_down = True
        tuition = tuition_cache.get(tx.tuition_id)
        account = account_map[tx.bank_account_id]
        items.append(
            {
                "transaction_id": tx.transaction_id,
                "bank_account_id": tx.bank_account_id,
                "tuition_id": tx.tuition_id,
                "amount": tx.amount,
                "status": tx.status,
                "created_at": tx.created_at,
                "completed_at": tx.completed_at,
                "failure_reason": tx.failure_reason,
                "bank_name": account["bank_name"],
                "account_num": "******" + str(account["account_num"])[-4:],
                "student_id": tuition["student_id"] if tuition else None,
                "student_name": tuition["student_name"] if tuition else None,
                "semester": tuition["semester"] if tuition else None,
            }
        )
    return items


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_payment(
    transaction_id: int,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    return _get_owned_transaction(db, transaction_id, user_id)
    