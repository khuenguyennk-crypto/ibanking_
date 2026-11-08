from conftest import (
    TUITIONS,
    balance_of,
    confirm,
    create_payment,
    expire_otp,
    latest_otp,
    movements_of,
    pay,
    tuition_row,
)


def test_payment_success(client, an):
    tx = pay(client, an, account_id=1, tuition_id=1)

    assert tx["status"] == "success"
    assert balance_of(1) == 20_000_000 - TUITIONS[1]
    tuition = tuition_row(1)
    assert tuition["status"] == "paid"
    assert tuition["paid_transaction_id"] == tx["transaction_id"]
    assert movements_of(tx["transaction_id"]) == [(1, "debit", TUITIONS[1])]

    history = client.get("/api/payments", headers=an).json()
    assert history[0]["transaction_id"] == tx["transaction_id"]
    assert history[0]["status"] == "success"


def test_cannot_pay_tuition_twice(client, an):
    pay(client, an, account_id=1, tuition_id=3)
    res = create_payment(client, an, account_id=1, tuition_id=3)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "TUITION_ALREADY_PAID"


def test_insufficient_balance(client, binh):
    res = create_payment(client, binh, account_id=3, tuition_id=1)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "INSUFFICIENT_BALANCE"
    assert balance_of(3) == 10_000_000


def test_cannot_use_other_users_account(client, an):
    res = create_payment(client, an, account_id=3, tuition_id=1)
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ACCOUNT_NOT_OWNED"


def test_wrong_otp(client, an):
    tx_id = create_payment(client, an, 1, 1).json()["transaction_id"]
    real = latest_otp(tx_id)
    wrong = "000000" if real != "000000" else "111111"

    res = confirm(client, an, tx_id, wrong)
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "OTP_INVALID"

    res = confirm(client, an, tx_id, real)
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_expired_otp_expires_transaction(client, an):
    tx_id = create_payment(client, an, 1, 1).json()["transaction_id"]
    code = latest_otp(tx_id)
    expire_otp(tx_id)

    res = confirm(client, an, tx_id, code)
    assert res.status_code == 400
    assert res.json()["error"]["code"] == "OTP_EXPIRED"
    assert client.get(f"/api/payments/{tx_id}", headers=an).json()["status"] == "expired"
    assert balance_of(1) == 20_000_000
    assert tuition_row(1)["status"] == "unpaid"


def test_resend_otp_invalidates_old_code(client, an):
    tx_id = create_payment(client, an, 1, 1).json()["transaction_id"]
    old_code = latest_otp(tx_id)

    res = client.post(f"/api/payments/{tx_id}/resend-otp", headers=an)
    assert res.status_code == 200
    new_code = latest_otp(tx_id)

    if old_code != new_code:
        res = confirm(client, an, tx_id, old_code)
        assert res.status_code == 400
    res = confirm(client, an, tx_id, new_code)
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_otp_used_once(client, an):
    tx = pay(client, an, 1, 1)
    code = latest_otp(tx["transaction_id"])

    res = confirm(client, an, tx["transaction_id"], code)
    assert res.status_code == 200
    assert balance_of(1) == 20_000_000 - TUITIONS[1]
    assert len(movements_of(tx["transaction_id"])) == 1


def test_cancel_payment(client, an):
    tx_id = create_payment(client, an, 1, 1).json()["transaction_id"]
    res = client.post(f"/api/payments/{tx_id}/cancel", headers=an)
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"

    res = confirm(client, an, tx_id, latest_otp(tx_id))
    assert res.status_code == 409
    assert balance_of(1) == 20_000_000
