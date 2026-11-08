from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TuitionItem(BaseModel):
    tuition_id: int
    semester: str
    amount: Decimal
    status: Literal["unpaid", "paid"]

    model_config = {"from_attributes": True}


class StudentTuitionResponse(BaseModel):
    student_id: str
    full_name: str
    tuitions: list[TuitionItem]



class TuitionInternal(BaseModel):
    tuition_id: int
    student_id: str
    student_name: str
    semester: str
    amount: Decimal
    status: Literal["unpaid", "paid"]
    paid_transaction_id: Optional[int] = None


class PayRequest(BaseModel):
    transaction_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)


class PayResponse(BaseModel):
    tuition_id: int
    status: Literal["unpaid", "paid"]
    paid_transaction_id: Optional[int] = None
    paid_at: Optional[datetime] = None
    already_processed: bool
