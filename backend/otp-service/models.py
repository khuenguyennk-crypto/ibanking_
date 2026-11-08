from sqlalchemy import BigInteger, Boolean, Column, DateTime, String
from db import Base


class Otp(Base):
    __tablename__ = "otps"

    otp_id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id = Column(BigInteger, nullable=False)
    otp_code = Column(String(6), nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)
    