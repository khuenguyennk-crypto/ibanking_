import os
import time
from pathlib import Path
import httpx
import pymysql
import pytest


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

_load_env_file()



BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")
DEMO_PASSWORD = "123456"

DB_CONFIG = {
    "host": os.getenv("TEST_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("TEST_DB_PORT", "3308")),
    "user": "root",
    "password": os.getenv("MYSQL_ROOT_PASSWORD", ""),
    "charset": "utf8mb4",
    "autocommit": True,
}

SEED_BALANCES = {1: 20_000_000, 2: 50_000_000, 3: 10_000_000, 4: 30_000_000, 5: 15_000_000}
TUITIONS = {1: 12_000_000, 2: 15_000_000, 3: 9_500_000, 4: 18_000_000}

FINAL_STATUSES = {"success", "failed", "expired", "cancelled"}

def db_query(sql: str, params=None):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()

def reset_data() -> None:
    db_query("DELETE FROM payment_db.transactions")
    db_query("DELETE FROM otp_db.otps")
    db_query("DELETE FROM account_db.balance_movements")
    for account_id, balance in SEED_BALANCES.items():
        db_query(
            "UPDATE account_db.accounts SET balance = %s WHERE bank_account_id = %s",
            (balance, account_id),
        )
    db_query(
        "UPDATE tuition_db.tuitions SET status = 'unpaid', paid_transaction_id = NULL, paid_at = NULL"
    )

def balance_of(account_id: int) -> int:
    rows = db_query("SELECT balance FROM account_db.accounts WHERE bank_account_id = %s", (account_id,))
    return int(rows[0][0])

def tuition_row(tuition_id: int) -> dict:
    rows = db_query(
        "SELECT status, paid_transaction_id FROM tuition_db.tuitions WHERE tuition_id = %s",
        (tuition_id,),
    )
    return {"status": rows[0][0], "paid_transaction_id": rows[0][1]}



def latest_otp(transaction_id: int) -> str:
    rows = db_query(
        "SELECT otp_code FROM otp_db.otps WHERE transaction_id = %s ORDER BY otp_id DESC LIMIT 1",
        (transaction_id,),
    )
    assert rows, f"Giao dịch {transaction_id} chưa có OTP"
    return rows[0][0]

def expire_otp(transaction_id: int) -> None:
    db_query(
        "UPDATE otp_db.otps SET expires_at = UTC_TIMESTAMP() - INTERVAL 1 MINUTE WHERE transaction_id = %s",
        (transaction_id,),
    )

def movements_of(transaction_id: int) -> list:
    rows = db_query(
        "SELECT bank_account_id, type, amount FROM account_db.balance_movements WHERE transaction_id = %s",
        (transaction_id,),
    )
    return [(r[0], r[1], int(r[2])) for r in rows]



def new_client() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL, timeout=60)

def login(client: httpx.Client, username: str) -> dict:
    res = client.post("/api/auth/login", json={"username": username, "password": DEMO_PASSWORD})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}



def create_payment(client, headers, account_id: int, tuition_id: int) -> httpx.Response:
    return client.post(
        "/api/payments",
        json={"bank_account_id": account_id, "tuition_id": tuition_id},
        headers=headers,
    )

def confirm(client, headers, transaction_id: int, otp_code: str) -> httpx.Response:
    return client.post(
        f"/api/payments/{transaction_id}/confirm",
        json={"otp_code": otp_code},
        headers=headers,
    )

def wait_final(client, headers, transaction_id: int, timeout: float = 90) -> dict:
    deadline = time.time() + timeout
    while True:
        tx = client.get(f"/api/payments/{transaction_id}", headers=headers).json()
        if tx["status"] in FINAL_STATUSES or time.time() > deadline:
            return tx
        time.sleep(1)

def pay(client, headers, account_id: int, tuition_id: int) -> dict:
    created = create_payment(client, headers, account_id, tuition_id)
    assert created.status_code == 201, created.text
    tx_id = created.json()["transaction_id"]
    res = confirm(client, headers, tx_id, latest_otp(tx_id))
    assert res.status_code in (200, 202), res.text
    return wait_final(client, headers, tx_id)



@pytest.fixture(autouse=True)
def _clean_data():
    reset_data()
    yield



@pytest.fixture
def client():
    with new_client() as c:
        yield c

@pytest.fixture
def an(client):
    return login(client, "an")

@pytest.fixture
def binh(client):
    return login(client, "binh")

@pytest.fixture
def cuong(client):
    return login(client, "cuong")
