# iBanking - Đóng học phí

Bài giữa kỳ môn Kiến trúc hướng dịch vụ (504070).

Người dùng đăng nhập, nhập MSSV để xem học phí, chọn tài khoản ngân hàng để trả, nhập OTP gửi qua email để xác nhận, sau đó xem kết quả và lịch sử giao dịch.

## Các service

| Service | Làm gì | DB | Port |
|---|---|---|---|
| frontend | Giao diện React, Nginx chuyển `/api` tới các service | | 3000 |
| user-service | Đăng nhập, thông tin người dùng | user_db | 8001 |
| account-service | Tài khoản ngân hàng, trừ tiền, hoàn tiền | account_db | 8002 |
| tuition-service | Sinh viên, học phí | tuition_db | 8003 |
| payment-service | Giao dịch, điều phối thanh toán, lịch sử | payment_db | 8004 |
| otp-service | OTP và gửi email | otp_db | 8005 |
| db | MySQL 8.0 | | 3308 |

Backend viết bằng FastAPI, mỗi service một database riêng. Các service gọi nhau qua API `/internal/...`, có header `X-Internal-Key`.

## Cần cài

- Docker Desktop
- Node.js và Python 3 (chỉ cần nếu chạy test)

## Chạy project

Tạo file `.env` ở thư mục gốc, copy từ `.env.example` rồi điền:

```
MYSQL_ROOT_PASSWORD=root_pw
USER_DB_PASSWORD=user_pw
ACCOUNT_DB_PASSWORD=account_pw
TUITION_DB_PASSWORD=tuition_pw
PAYMENT_DB_PASSWORD=payment_pw
OTP_DB_PASSWORD=otp_pw

JWT_SECRET=...
INTERNAL_KEY=...

OTP_VALID_SECONDS=300

SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
```

Mật khẩu các DB phải đúng như trên vì đã tạo sẵn trong `backend/sql/01-db.sql`, còn `MYSQL_ROOT_PASSWORD` thì đặt gì cũng được. `JWT_SECRET` và `INTERNAL_KEY` có thể sinh bằng lệnh ở cuối `.env.example`.

SMTP để trống thì email không gửi thật mà in ra log. Muốn gửi bằng Gmail thì điền `smtp.gmail.com`, email và App Password của Gmail.

Sau đó chạy:

```
docker compose up -d --build
```

Lần đầu hơi lâu, MySQL cũng cần khoảng nửa phút để tạo database. Xem trạng thái bằng `docker compose ps`.

Vào http://localhost:3000

## Tài khoản demo

Mật khẩu đều là `123456`.

| User | Ngân hàng | Số dư |
|---|---|---|
| an | Vietcombank | 20.000.000 |
| an | MB Bank | 50.000.000 |
| binh | Techcombank | 10.000.000 |
| binh | BIDV | 30.000.000 |
| cuong | ACB | 15.000.000 |

MSSV để tra: `520H0001` đến `520H0004`.

## Cách dùng

1. Đăng nhập.
2. Vào Thanh toán, nhập MSSV.
3. Chọn tài khoản để trả, tick đồng ý điều khoản rồi bấm xác nhận.
4. Nhập OTP (hiệu lực 5 phút, dùng 1 lần, có nút gửi lại).
5. Xem kết quả. Các giao dịch cũ ở mục Lịch sử.

Nếu không cấu hình SMTP thì lấy OTP ở đây:

```
docker compose logs -f otp-service
```

## API

Khi đang chạy, mỗi service có trang Swagger:

- http://localhost:8001/docs (user)
- http://localhost:8002/docs (account)
- http://localhost:8003/docs (tuition)
- http://localhost:8004/docs (payment)
- http://localhost:8005/docs (otp)

## Test

Test tự động nằm trong `tests/e2e`, dùng pytest. Phải bật hệ thống trước.

```
npm run test:install
npm test
```

Lệnh đầu chỉ cần chạy một lần để cài thư viện. Muốn chạy riêng test đồng thời thì dùng `npm run test:concurrency`.

Test sẽ reset dữ liệu trước mỗi lần chạy (xóa giao dịch, trả số dư và học phí về như cũ). Muốn tự reset sau khi test tay thì:

```
npm run db:reset
```

## Tắt

```
docker compose down
```

Thêm `-v` nếu muốn xóa luôn database. Sửa `01-db.sql` thì phải chạy `docker compose down -v` rồi bật lại mới nhận database đã sửa.

