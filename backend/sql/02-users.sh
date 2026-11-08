set -e

mysql --protocol=socket -uroot -p"$MYSQL_ROOT_PASSWORD" -e "
CREATE USER IF NOT EXISTS 'user_admin'@'%' IDENTIFIED BY '${USER_DB_PASSWORD}';
CREATE USER IF NOT EXISTS 'account_admin'@'%' IDENTIFIED BY '${ACCOUNT_DB_PASSWORD}';
CREATE USER IF NOT EXISTS 'tuition_admin'@'%' IDENTIFIED BY '${TUITION_DB_PASSWORD}';
CREATE USER IF NOT EXISTS 'payment_admin'@'%' IDENTIFIED BY '${PAYMENT_DB_PASSWORD}';
CREATE USER IF NOT EXISTS 'otp_admin'@'%' IDENTIFIED BY '${OTP_DB_PASSWORD}';

GRANT ALL PRIVILEGES ON user_db.* TO 'user_admin'@'%';
GRANT ALL PRIVILEGES ON account_db.* TO 'account_admin'@'%';
GRANT ALL PRIVILEGES ON tuition_db.* TO 'tuition_admin'@'%';
GRANT ALL PRIVILEGES ON payment_db.* TO 'payment_admin'@'%';
GRANT ALL PRIVILEGES ON otp_db.* TO 'otp_admin'@'%';
FLUSH PRIVILEGES;
"
