from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import get_db
from models import Account, BalanceMovement
from schemas import (
    AccountInternal,
    AccountMasked,
    AccountPublic,
    DebitRequest,
    MovementResponse,
    RefundRequest,
    RevealRequest,
)
from security import get_current_user_id, verify_internal_key
import user_client

router = APIRouter(tags=["Tài khoản ngân hàng"])



def _account_not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "ACCOUNT_NOT_FOUND", "message": "Không tìm thấy tài khoản"},
    )


def _find_movement(db: Session, transaction_id: int, move_type: str):
    return (
        db.query(BalanceMovement)
        .filter(
            BalanceMovement.transaction_id == transaction_id,
            BalanceMovement.type == move_type,
        )
        .first()
    )


def _current_balance(db: Session, account_id: int):
    return db.query(Account.balance).filter(Account.bank_account_id == account_id).scalar()


def _movement_response(movement: BalanceMovement, balance, already_processed: bool) -> dict:
    return {
        "bank_account_id": movement.bank_account_id,
        "transaction_id": movement.transaction_id,
        "type": movement.type,
        "amount": movement.amount,
        "balance": balance,
        "already_processed": already_processed,
    }


def _check_same_account(movement: BalanceMovement, account_id: int) -> None:
    if movement.bank_account_id != account_id:
        raise HTTPException(
            status_code=409,
            detail={"code": "TRANSACTION_ACCOUNT_MISMATCH", "message": "Giao dịch này đã gắn với một tài khoản khác",},
        )


def _commit_and_respond(db: Session, account_id: int, transaction_id: int, move_type: str) -> dict:
    try:
        db.commit()
        already_processed = False
    except IntegrityError:
        db.rollback()
        already_processed = True

    movement = _find_movement(db, transaction_id, move_type)
    if movement is None:
        raise HTTPException(
            status_code=500,
            detail={"code": "MOVEMENT_FAILED", "message": "Không ghi được biến động số dư"},
        )
    return _movement_response(movement, _current_balance(db, account_id), already_processed)



def _mask(account_num: str) -> str:
    return "******" + str(account_num)[-4:]


@router.get("/api/accounts", response_model=list[AccountMasked])
def list_my_accounts(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    accounts = (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .order_by(Account.bank_account_id)
        .all()
    )
    return [
        {
            "bank_account_id": a.bank_account_id,
            "bank_name": a.bank_name,
            "account_num": _mask(a.account_num),
            "balance": a.balance,
        }
        for a in accounts
    ]

@router.post("/api/accounts/{account_id}/reveal", response_model=AccountPublic)
def reveal_account(
    account_id: int,
    body: RevealRequest,
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    account = db.get(Account, account_id)
    if account is None or account.user_id != user_id:
        raise _account_not_found()

    if not user_client.verify_password(user_id, body.password):
        raise HTTPException(
            status_code=403,
            detail={"code": "INVALID_PASSWORD", "message": "Mật khẩu không đúng"},
        )
    return account


@router.get(
    "/internal/accounts",
    response_model=list[AccountInternal],
    dependencies=[Depends(verify_internal_key)],
)
def list_accounts_of_user(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Account)
        .filter(Account.user_id == user_id)
        .order_by(Account.bank_account_id)
        .all()
    )


@router.get(
    "/internal/accounts/{account_id}",
    response_model=AccountInternal,
    dependencies=[Depends(verify_internal_key)],
)
def get_account(account_id: int, db: Session = Depends(get_db)):
    account = db.get(Account, account_id)
    if account is None:
        raise _account_not_found()
    return account


@router.post(
    "/internal/accounts/{account_id}/debit",
    response_model=MovementResponse,
    dependencies=[Depends(verify_internal_key)],
)
def debit(account_id: int, body: DebitRequest, db: Session = Depends(get_db)):
    if db.get(Account, account_id) is None:
        raise _account_not_found()

    old = _find_movement(db, body.transaction_id, "debit")
    if old is not None:
        _check_same_account(old, account_id)
        return _movement_response(old, _current_balance(db, account_id), True)

    result = db.execute(
        update(Account)
        .where(Account.bank_account_id == account_id, Account.balance >= body.amount)
        .values(balance=Account.balance - body.amount)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "INSUFFICIENT_BALANCE", "message": "Số dư không đủ"},
        )

    db.add(
        BalanceMovement(
            bank_account_id=account_id,
            transaction_id=body.transaction_id,
            type="debit",
            amount=body.amount,
        )
    )
    return _commit_and_respond(db, account_id, body.transaction_id, "debit")


@router.post(
    "/internal/accounts/{account_id}/refund",
    response_model=MovementResponse,
    dependencies=[Depends(verify_internal_key)],
)
def refund(account_id: int, body: RefundRequest, db: Session = Depends(get_db)):
    if db.get(Account, account_id) is None:
        raise _account_not_found()

    old = _find_movement(db, body.transaction_id, "refund")
    if old is not None:
        _check_same_account(old, account_id)
        return _movement_response(old, _current_balance(db, account_id), True)

    debit_movement = _find_movement(db, body.transaction_id, "debit")
    if debit_movement is None or debit_movement.bank_account_id != account_id:
        raise HTTPException(
            status_code=409,
            detail={"code": "DEBIT_NOT_FOUND", "message": "Giao dịch này chưa có lần trừ tiền để hoàn tiền"},
        )

    db.execute(
        update(Account)
        .where(Account.bank_account_id == account_id)
        .values(balance=Account.balance + debit_movement.amount)
        .execution_options(synchronize_session=False)
    )
    db.add(
        BalanceMovement(
            bank_account_id=account_id,
            transaction_id=body.transaction_id,
            type="refund",
            amount=debit_movement.amount,
        )
    )
    return _commit_and_respond(db, account_id, body.transaction_id, "refund")
    