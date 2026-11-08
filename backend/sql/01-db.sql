SET NAMES utf8mb4;

CREATE DATABASE IF NOT EXISTS user_db;
CREATE DATABASE IF NOT EXISTS account_db;
CREATE DATABASE IF NOT EXISTS tuition_db;
CREATE DATABASE IF NOT EXISTS payment_db;
CREATE DATABASE IF NOT EXISTS otp_db;

CREATE USER IF NOT EXISTS 'user_admin'@'%' IDENTIFIED BY 'user_pw';
CREATE USER IF NOT EXISTS 'account_admin'@'%' IDENTIFIED BY 'account_pw';
CREATE USER IF NOT EXISTS 'tuition_admin'@'%' IDENTIFIED BY 'tuition_pw';
CREATE USER IF NOT EXISTS 'payment_admin'@'%' IDENTIFIED BY 'payment_pw';
CREATE USER IF NOT EXISTS 'otp_admin'@'%' IDENTIFIED BY 'otp_pw';

GRANT ALL PRIVILEGES ON user_db.* TO 'user_admin'@'%';
GRANT ALL PRIVILEGES ON account_db.* TO 'account_admin'@'%';
GRANT ALL PRIVILEGES ON tuition_db.* TO 'tuition_admin'@'%';
GRANT ALL PRIVILEGES ON payment_db.* TO 'payment_admin'@'%';
GRANT ALL PRIVILEGES ON otp_db.* TO 'otp_admin'@'%';
FLUSH PRIVILEGES;

USE user_db;
CREATE TABLE users (
    user_id BIGINT  NOT NULL AUTO_INCREMENT,
    username    VARCHAR(50) NOT NULL,
    password_hash   VARCHAR(100)    NOT NULL,
    full_name   VARCHAR(100)    NOT NULL,
    phone   VARCHAR(20) NOT NULL,
    email   VARCHAR(100)    NOT NULL,
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY user_username (username)
);


USE account_db;
CREATE TABLE accounts (
    bank_account_id BIGINT  NOT NULL AUTO_INCREMENT,
    user_id BIGINT  NOT NULL,
    bank_name   VARCHAR(50) NOT NULL,
    account_num VARCHAR(30) NOT NULL,
    account_name    VARCHAR(100)    NOT NULL,
    balance DECIMAL(15,2)   NOT NULL DEFAULT 0,
    PRIMARY KEY (bank_account_id),
    CONSTRAINT check_balance CHECK (balance >= 0),
    KEY index_user (user_id)
);
CREATE TABLE balance_movements (
    movement_id BIGINT  NOT NULL AUTO_INCREMENT,
    bank_account_id BIGINT  NOT NULL,
    transaction_id  BIGINT  NOT NULL,
    type    ENUM('debit','refund')  NOT NULL,
    amount  DECIMAL(15,2)   NOT NULL,
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (movement_id),
    UNIQUE KEY movement_type (transaction_id, type),
    CONSTRAINT check_balance_amount CHECK (amount > 0),
    CONSTRAINT fk_movement_account FOREIGN KEY (bank_account_id) REFERENCES accounts (bank_account_id)
);

INSERT INTO accounts (bank_account_id, user_id, bank_name, account_num, account_name, balance) VALUES
(1, 1, 'Vietcombank', '97864527345818', 'NGUYEN VAN AN', 20000000.00),
(2, 1, 'MB Bank', '53078193034401', 'NGUYEN VAN AN', 50000000.00),
(3, 2, 'Techcombank', '86913678580203', 'TRAN THI BINH', 10000000.00),
(4, 2, 'BIDV', '31410001234567', 'TRAN THI BINH', 30000000.00),
(5, 3, 'ACB', '60200944822412', 'LE QUANG CUONG', 15000000.00);


USE tuition_db;
CREATE TABLE students (
    student_id  VARCHAR(20) NOT NULL,
    full_name   VARCHAR(100)    NOT NULL,
    PRIMARY KEY (student_id)
);
CREATE TABLE tuitions (
    tuition_id  BIGINT  NOT NULL AUTO_INCREMENT,
    student_id  VARCHAR(20) NOT NULL,
    semester    VARCHAR(20) NOT NULL,
    amount  DECIMAL(15,2)   NOT NULL,
    status  ENUM('unpaid','paid')   NOT NULL DEFAULT 'unpaid',
    paid_transaction_id BIGINT  NULL,
    paid_at DATETIME    NULL,
    PRIMARY KEY (tuition_id),
    UNIQUE KEY tuition_per_semester (student_id, semester),
    CONSTRAINT check_tuition_amount CHECK (amount > 0),
    CONSTRAINT fk_tuition_student FOREIGN KEY (student_id) REFERENCES students (student_id)
);

INSERT INTO students (student_id, full_name) VALUES
('520H0001', 'Phạm Văn An'),
('520H0002', 'Võ Thị Bình'),
('520H0003', 'Đặng Văn Cường'),
('520H0004', 'Bùi Thị Diệu');
 
INSERT INTO tuitions (student_id, semester, amount, status) VALUES
('520H0001', 'HK1-2026-2027', 12000000.00, 'unpaid'),
('520H0002', 'HK1-2026-2027', 15000000.00, 'unpaid'),
('520H0003', 'HK1-2026-2027', 9500000.00, 'unpaid'),
('520H0004', 'HK1-2026-2027', 18000000.00, 'unpaid');


USE payment_db;
CREATE TABLE transactions (
    transaction_id  BIGINT  NOT NULL AUTO_INCREMENT,
    bank_account_id BIGINT  NOT NULL,
    tuition_id  BIGINT  NOT NULL,
    amount  DECIMAL(15,2)   NOT NULL,
    status  ENUM('pending','otp_sent','processing','success','failed','expired', 'cancelled')    NOT NULL DEFAULT 'pending',
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME    NULL,
    failure_reason  VARCHAR(255)    NULL,
    PRIMARY KEY (transaction_id),
    CONSTRAINT check_transaction_amount CHECK (amount > 0),
    KEY index_bank_account (bank_account_id),
    KEY index_tuition (tuition_id)
);


USE otp_db;
CREATE TABLE otps (
    otp_id  BIGINT  NOT NULL AUTO_INCREMENT,
    transaction_id  BIGINT  NOT NULL,
    otp_code    VARCHAR(6)  NOT NULL,
    created_at  DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at  DATETIME    NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (otp_id),
    KEY index_transaction (transaction_id),
    KEY index_code (otp_code)
);