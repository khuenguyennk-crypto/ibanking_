from sqlalchemy import BigInteger, Column, DateTime, Enum, Numeric, String
from db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(BigInteger, primary_key=True, autoincrement=True)
    bank_account_id = Column(BigInteger, nullable=False)
    tuition_id = Column(BigInteger, nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(
        Enum("pending", "otp_sent", "processing", "success", "failed", "expired", "cancelled", name="transaction_status"),
        nullable=False,
        default="pending",
    )
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    failure_reason = Column(String(255), nullable=True)
    