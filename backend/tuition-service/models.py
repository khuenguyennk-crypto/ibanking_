from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Numeric, String
from db import Base


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(20), primary_key=True)
    full_name = Column(String(100), nullable=False)


class Tuition(Base):
    __tablename__ = "tuitions"

    tuition_id = Column(BigInteger, primary_key=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    semester = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    status = Column(Enum("unpaid", "paid", name="tuition_status"), nullable=False, default="unpaid")
    paid_transaction_id = Column(BigInteger, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    