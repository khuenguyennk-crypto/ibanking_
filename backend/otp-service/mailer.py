import logging
import os
import smtplib
from decimal import Decimal
from email.message import EmailMessage

logger = logging.getLogger("mailer")

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT") or 587)
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM") or SMTP_USER


class MailError(Exception):
    pass

def send_email(to: str, subject: str, body: str) -> None:
    if not SMTP_HOST:
        print(f"\nDev mail:\nTo: {to}\nSubject: {subject}\n\n{body}\n---\n", flush=True)
        return

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
            server.starttls()
        with server:
            if SMTP_USER:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        logger.error("Gửi email tới %s thất bại: %s", to, exc)
        raise MailError(str(exc)) from exc


def send_otp_email(to: str, full_name: str, code: str, minutes: int) -> None:
    body = (
        f"Xin chào {full_name or 'quý khách'},\n\n"
        f"Mã OTP xác nhận thanh toán học phí iBanking của bạn là: {code}\n"
        f"Mã có hiệu lực trong {minutes} phút và chỉ dùng được một lần.\n"
        f"Tuyệt đối không chia sẻ mã này cho bất kỳ ai.\n"
    )
    send_email(to, "Mã OTP xác nhận thanh toán học phí", body)


def send_success_email(
    to: str,
    full_name: str,
    transaction_id: int,
    student_id: str,
    student_name: str,
    semester: str,
    amount: Decimal,
) -> None:
    money = f"{amount:,.0f}".replace(",", ".")
    body = (
        f"Xin chào {full_name or 'quý khách'},\n\n"
        f"Giao dịch thanh toán học phí của bạn đã thành công.\n\n"
        f"Mã giao dịch : {transaction_id}\n"
        f"MSSV         : {student_id}\n"
        f"Sinh viên    : {student_name}\n"
        f"Học kỳ       : {semester}\n"
        f"Số tiền      : {money} VND\n\n"
        f"Cảm ơn bạn đã sử dụng iBanking.\n"
    )
    send_email(to, "Xác nhận thanh toán học phí thành công", body)
