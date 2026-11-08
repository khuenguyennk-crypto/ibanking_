from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, update
from sqlalchemy.orm import Session

from db import get_db
from models import Student, Tuition
from schemas import PayRequest, PayResponse, StudentTuitionResponse, TuitionInternal
from security import get_current_user_id, verify_internal_key

router = APIRouter(tags=["Học phí"])


def _tuition_not_found() -> HTTPException:
    return HTTPException(
        status_code=404,
        detail={"code": "TUITION_NOT_FOUND", "message": "Không tìm thấy khoản học phí"},
    )


def _pay_response(t: Tuition, already_processed: bool) -> dict:
    return {
        "tuition_id": t.tuition_id,
        "status": t.status,
        "paid_transaction_id": t.paid_transaction_id,
        "paid_at": t.paid_at,
        "already_processed": already_processed,
    }



@router.get("/api/tuitions/{student_id}", response_model=StudentTuitionResponse)
def lookup_by_student_id(
    student_id: str,
    _user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    student_id = student_id.strip()
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "STUDENT_NOT_FOUND", "message": "Không tìm thấy sinh viên với MSSV này"},
        )
    tuitions = (
        db.query(Tuition)
        .filter(Tuition.student_id == student_id)
        .order_by(Tuition.tuition_id)
        .all()
    )
    return {"student_id": student.student_id, "full_name": student.full_name, "tuitions": tuitions}





@router.get(
    "/internal/tuitions/{tuition_id}",
    response_model=TuitionInternal,
    dependencies=[Depends(verify_internal_key)],
)
def get_tuition(tuition_id: int, db: Session = Depends(get_db)):
    row = (
        db.query(Tuition, Student.full_name)
        .join(Student, Student.student_id == Tuition.student_id)
        .filter(Tuition.tuition_id == tuition_id)
        .first()
    )
    if row is None:
        raise _tuition_not_found()
    tuition, student_name = row
    return {
        "tuition_id": tuition.tuition_id,
        "student_id": tuition.student_id,
        "student_name": student_name,
        "semester": tuition.semester,
        "amount": tuition.amount,
        "status": tuition.status,
        "paid_transaction_id": tuition.paid_transaction_id,
    }


@router.post(
    "/internal/tuitions/{tuition_id}/pay",
    response_model=PayResponse,
    dependencies=[Depends(verify_internal_key)],
)
def pay(tuition_id: int, body: PayRequest, db: Session = Depends(get_db)):
    result = db.execute(
        update(Tuition)
        .where(
            Tuition.tuition_id == tuition_id,
            Tuition.status == "unpaid",
            Tuition.amount == body.amount,
        )
        .values(status="paid", paid_at=func.now(), paid_transaction_id=body.transaction_id)
        .execution_options(synchronize_session=False)
    )
    if result.rowcount == 1:
        db.commit()
        fresh = db.query(Tuition).filter(Tuition.tuition_id == tuition_id).first()
        return _pay_response(fresh, already_processed=False)

    db.rollback()
    tuition = db.query(Tuition).filter(Tuition.tuition_id == tuition_id).first()

    if tuition is None:
        raise _tuition_not_found()

    if tuition.paid_transaction_id == body.transaction_id:
        return _pay_response(tuition, already_processed=True)

    if tuition.status == "paid":
        raise HTTPException(
            status_code=409,
            detail={"code": "TUITION_ALREADY_PAID", "message": "Khoản học phí đã được giao dịch khác thanh toán"},
        )

    raise HTTPException(
        status_code=409,
        detail={"code": "AMOUNT_MISMATCH", "message": "Số tiền không khớp với học phí cần đóng"},
    )
    