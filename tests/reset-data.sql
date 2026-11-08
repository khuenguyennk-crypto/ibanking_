DELETE FROM payment_db.transactions;
DELETE FROM otp_db.otps;
DELETE FROM account_db.balance_movements;

UPDATE account_db.accounts SET balance = CASE bank_account_id
    WHEN 1 THEN 20000000
    WHEN 2 THEN 50000000
    WHEN 3 THEN 10000000
    WHEN 4 THEN 30000000
    WHEN 5 THEN 15000000
END;

UPDATE tuition_db.tuitions SET status = 'unpaid', paid_transaction_id = NULL, paid_at = NULL;
