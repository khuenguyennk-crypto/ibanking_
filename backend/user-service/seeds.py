from db import SessionLocal
from models import User
from security import hash_password

SAMPLE_USERS = [
    {
        "user_id": 1,
        "username": "an",
        "full_name": "Nguyen Van An",
        "phone": "0901000001",
        "email": "an@example.com",
    },
    {
        "user_id": 2,
        "username": "binh",
        "full_name": "Tran Thi Binh",
        "phone": "0901000002",
        "email": "binh@example.com",
    },
    {
        "user_id": 3,
        "username": "cuong",
        "full_name": "Le Quang Cuong",
        "phone": "0901000003",
        "email": "cuong@example.com",
    },
]
DEMO_PASSWORD = "123456"


def seed_users() -> None:
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return
        for data in SAMPLE_USERS:
            db.add(User(**data, password_hash=hash_password(DEMO_PASSWORD)))
        db.commit()
    finally:
        db.close()
        