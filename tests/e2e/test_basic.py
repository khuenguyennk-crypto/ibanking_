from conftest import DEMO_PASSWORD


def test_login_ok(client):
    res = client.post("/api/auth/login", json={"username": "an", "password": DEMO_PASSWORD})
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"]
    assert body["user"]["user_id"] == 1


def test_login_wrong_password(client):
    res = client.post("/api/auth/login", json={"username": "an", "password": "sai-mat-khau"})
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_api_requires_token(client):
    res = client.get("/api/users/me")
    assert res.status_code == 401


def test_profile(client, an):
    res = client.get("/api/users/me", headers=an)
    assert res.status_code == 200
    body = res.json()
    assert body["full_name"] and body["phone"] and body["email"]


def test_list_accounts_only_mine(client, an):
    res = client.get("/api/accounts", headers=an)
    assert res.status_code == 200
    ids = [a["bank_account_id"] for a in res.json()]
    assert ids == [1, 2]


def test_lookup_tuition(client, an):
    res = client.get("/api/tuitions/520H0001", headers=an)
    assert res.status_code == 200
    body = res.json()
    assert body["full_name"]
    assert body["tuitions"][0]["status"] == "unpaid"
    assert float(body["tuitions"][0]["amount"]) == 12_000_000


def test_lookup_unknown_student(client, an):
    res = client.get("/api/tuitions/KHONGTONTAI", headers=an)
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "STUDENT_NOT_FOUND"
