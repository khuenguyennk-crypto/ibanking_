from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["pending", "otp_sent", "processing", "success", "failed", "expired", "cancelled"]


class CreatePaymentRequest(BaseModel):
    bank_account_id: int = Field(gt=0)
    tuition_id: int = Field(gt=0)


class CreatePaymentResponse(BaseModel):
    transaction_id: int
    status: Status
    amount: Decimal
    otp_expires_in: int


class ConfirmRequest(BaseModel):
    otp_code: str = Field(min_length=1, max_length=20)


class ResendOtpResponse(BaseModel):
    transaction_id: int
    status: Status
    otp_expires_in: int


class TransactionResponse(BaseModel):
    transaction_id: int
    bank_account_id: int
    tuition_id: int
    amount: Decimal
    status: Status
    created_at: datetime
    completed_at: Optional[datetime] = None
    failure_reason: Optional[str] = None

    model_config = {"from_attributes": True}


class HistoryItem(TransactionResponse):
    bank_name: Optional[str] = None
    account_num: Optional[str] = None
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    semester: Optional[str] = None
    