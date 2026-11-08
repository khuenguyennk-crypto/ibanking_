from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Numeric, String, func
from db import Base


class Account(Base):
    __tablename__ = "accounts"

    bank_account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    bank_name = Column(String(50), nullable=False)
    account_num = Column(String(30), nullable=False)
    account_name = Column(String(100), nullable=False)
    balance = Column(Numeric(15, 2), nullable=False, default=0)


class BalanceMovement(Base):
    __tablename__ = "balance_movements"

    movement_id = Column(BigInteger, primary_key=True, autoincrement=True)
    bank_account_id = Column(BigInteger, ForeignKey("accounts.bank_account_id"), nullable=False)
    transaction_id = Column(BigInteger, nullable=False)
    type = Column(Enum("debit", "refund", name="movement_type"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    