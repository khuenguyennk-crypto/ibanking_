from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OtpCreateRequest(BaseModel):
    transaction_id: int = Field(gt=0)
    email: str = Field(min_length=3, max_length=100)
    full_name: str = Field(default="", max_length=100)


class OtpCreated(BaseModel):
    transaction_id: int
    expires_at: datetime
    expires_in: int


class OtpVerifyRequest(BaseModel):
    transaction_id: int = Field(gt=0)
    otp_code: str = Field(min_length=1, max_length=20)


class OtpVerified(BaseModel):
    transaction_id: int
    valid: bool


class PaymentSuccessNotification(BaseModel):
    transaction_id: int = Field(gt=0)
    email: str = Field(min_length=3, max_length=100)
    full_name: str = Field(default="", max_length=100)
    student_id: str
    student_name: str
    semester: str
    amount: Decimal
    