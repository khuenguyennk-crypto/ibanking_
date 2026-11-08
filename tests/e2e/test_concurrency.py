import threading

from conftest import (
    SEED_BALANCES,
    TUITIONS,
    balance_of,
    confirm,
    create_payment,
    latest_otp,
    login,
    movements_of,
    new_client,
    tuition_row,
    wait_final,
)


def _confirm_all_at_once(jobs):
    barrier = threading.Barrier(len(jobs))
    results = [None] * len(jobs)

    def worker(index, username, tx_id, code):
        with new_client() as c:
            headers = login(c, username)
            barrier.wait()
            res = confirm(c, headers, tx_id, code)
            assert res.status_code in (200, 202), res.text
            results[index] = wait_final(c, headers, tx_id)

    threads = []
    for i, (username, tx_id) in enumerate(jobs):
        t = threading.Thread(target=worker, args=(i, username, tx_id, latest_otp(tx_id)))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return results


def test_same_account_cannot_overspend(client, an):
    tx_ids = []
    for tuition_id in (1, 2, 3):
        res = create_payment(client, an, account_id=1, tuition_id=tuition_id)
        assert res.status_code == 201, res.text
        tx_ids.append(res.json()["transaction_id"])

    results = _confirm_all_at_once([("an", tx_id) for tx_id in tx_ids])

    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    assert len(success) == 1, results
    assert len(failed) == 2, results

    spent = TUITIONS[success[0]["tuition_id"]]
    assert balance_of(1) == SEED_BALANCES[1] - spent
    assert balance_of(1) >= 0
    for r in failed:
        assert tuition_row(r["tuition_id"])["status"] == "unpaid"


def test_same_tuition_paid_only_once(client, an, binh, cuong):
    payers = [("an", an, 1), ("binh", binh, 3), ("cuong", cuong, 5)]
    jobs = []
    for username, headers, account_id in payers:
        res = create_payment(client, headers, account_id=account_id, tuition_id=3)
        assert res.status_code == 201, res.text
        jobs.append((username, res.json()["transaction_id"]))

    results = _confirm_all_at_once(jobs)

    success = [r for r in results if r["status"] == "success"]
    failed = [r for r in results if r["status"] == "failed"]
    assert len(success) == 1, results
    assert len(failed) == 2, results

    tuition = tuition_row(3)
    assert tuition["status"] == "paid"
    assert tuition["paid_transaction_id"] == success[0]["transaction_id"]

    winner_account = success[0]["bank_account_id"]
    for _, _, account_id in payers:
        expected = SEED_BALANCES[account_id] - (TUITIONS[3] if account_id == winner_account else 0)
        assert balance_of(account_id) == expected

    for r in failed:
        types = sorted(m[1] for m in movements_of(r["transaction_id"]))
        assert types in ([], ["debit", "refund"]), types
