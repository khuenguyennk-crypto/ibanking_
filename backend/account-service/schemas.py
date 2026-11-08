from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class AccountPublic(BaseModel):
    bank_account_id: int
    bank_name: str
    account_num: str
    account_name: str
    balance: Decimal

    model_config = {"from_attributes": True}


class AccountMasked(BaseModel):
    bank_account_id: int
    bank_name: str
    account_num: str
    balance: Decimal


class RevealRequest(BaseModel):
    password: str = Field(min_length=1)


class AccountInternal(AccountPublic):
    user_id: int


class DebitRequest(BaseModel):
    transaction_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=15, decimal_places=2)


class RefundRequest(BaseModel):
    transaction_id: int = Field(gt=0)


class MovementResponse(BaseModel):
    bank_account_id: int
    transaction_id: int
    type: Literal["debit", "refund"]
    amount: Decimal
    balance: Decimal
    already_processed: bool
    