import logging

from fastapi import APIRouter, BackgroundTasks, Depends

from mailer import MailError, send_success_email
from schemas import PaymentSuccessNotification
from security import verify_internal_key

router = APIRouter(tags=["Thông báo"], dependencies=[Depends(verify_internal_key)])
logger = logging.getLogger("notifications")


def _send_safely(body: PaymentSuccessNotification) -> None:
    try:
        send_success_email(
            to=body.email,
            full_name=body.full_name,
            transaction_id=body.transaction_id,
            student_id=body.student_id,
            student_name=body.student_name,
            semester=body.semester,
            amount=body.amount,
        )
    except MailError:
        logger.error("Không gửi được email xác nhận cho giao dịch %s", body.transaction_id)


@router.post("/internal/notifications/payment-success", status_code=202)
def payment_success(body: PaymentSuccessNotification, background: BackgroundTasks):
    background.add_task(_send_safely, body)
    return {"accepted": True}
    