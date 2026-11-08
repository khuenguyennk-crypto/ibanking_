# iBanking

Bài giữa kỳ môn Kiến trúc hướng dịch vụ (504070).

Người dùng đăng nhập, nhập MSSV để xem học phí, chọn tài khoản ngân hàng để trả, nhập OTP gửi qua email để xác nhận, sau đó xem kết quả và lịch sử giao dịch.

## Các service

| Service | Thực hiện | DB | Port |
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
MYSQL_ROOT_PASSWORD=...
USER_DB_PASSWORD=...
ACCOUNT_DB_PASSWORD=...
TUITION_DB_PASSWORD=...
PAYMENT_DB_PASSWORD=...
OTP_DB_PASSWORD=...

JWT_SECRET=...
INTERNAL_KEY=...

OTP_VALID_SECONDS=300

SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
```

Mật khẩu DB đặt tùy ý, nên chỉ dùng chữ và số. Lúc khởi tạo, MySQL chạy `backend/sql/01-db.sql` để tạo database, bảng và dữ liệu mẫu, sau đó chạy `backend/sql/02-users.sh` để tạo user cho từng service với mật khẩu lấy từ `.env`.

`JWT_SECRET` và `INTERNAL_KEY` nên là chuỗi dài, ngẫu nhiên. Có thể sinh bằng lệnh dưới đây rồi copy kết quả vào `.env`.

PowerShell:

```powershell
function New-Key { $b = New-Object byte[] 32; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b); -join ($b | ForEach-Object { $_.ToString("x2") }) }
"JWT_SECRET=$(New-Key)"; "INTERNAL_KEY=$(New-Key)"
```

CMD:

```cmd
powershell -NoProfile -Command "function K{$b=New-Object byte[] 32;[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($b);-join($b|%{$_.ToString('x2')})}; 'JWT_SECRET='+(K); 'INTERNAL_KEY='+(K)"
```

Nếu để trống `SMTP_HOST` thì hệ thống không gửi email thật. Nội dung email (gồm mã OTP) được in ra log của otp-service, xem bằng `docker compose logs -f otp-service`. Cách này đủ để chạy thử và demo.

Muốn gửi email thật qua Gmail thì điền vào `.env`:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tencuaban@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
SMTP_FROM=tencuaban@gmail.com
```

- `SMTP_USER`: địa chỉ Gmail dùng để gửi.
- `SMTP_PASSWORD`: không phải mật khẩu đăng nhập Gmail, mà là App Password (mật khẩu ứng dụng) gồm 16 ký tự. Muốn tạo thì tài khoản Google phải bật xác minh 2 bước, sau đó vào https://myaccount.google.com/apppasswords, đặt tên bất kỳ rồi copy mã được cấp. Bỏ các dấu cách giữa các nhóm ký tự khi dán vào.
- `SMTP_FROM`: địa chỉ hiện ở mục người gửi, thường để giống `SMTP_USER`.

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

Ghi chú: Số tài khoản trong dữ liệu mẫu (`backend/sql/01-db.sql`) là số được sinh ngẫu nhiên bằng:

```powershell
-join (1..14 | % { Get-Random -Max 10 })
```

CMD:

```cmd
powershell -c "-join (1..14 | % { Get-Random -Max 10 })"
```

`14` là số chữ số trong dãy output sinh ra sau khi chạy lệnh.

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

Test tự động viết bằng pytest, nằm trong thư mục `tests/e2e`. Test gọi API thật qua http://localhost:3000 giống như frontend, đồng thời đọc thẳng MySQL (cổng 3308) để lấy mã OTP và kiểm tra số dư, trạng thái học phí sau mỗi giao dịch.

Trước khi chạy test:

- Hệ thống phải đang chạy (`docker compose up -d`, các service đều `Up`).
- File `.env` phải có `MYSQL_ROOT_PASSWORD`, vì test dùng tài khoản root để đọc và reset dữ liệu.
- Máy có Node.js (để chạy lệnh `npm`) và Python 3. Nếu máy gõ `py` mới chạy được Python thì sửa `python` thành `py` trong `package.json`.

Các lệnh, chạy ở thư mục gốc:

| Lệnh | Thực hiện |
|---|---|
| `npm run test:install` | Cài thư viện cho test (pytest, httpx, pymysql). Chỉ cần chạy lần đầu |
| `npm test` | Chạy toàn bộ test |
| `npm run test:concurrency` | Chỉ chạy 2 test đồng thời |
| `npm run db:reset` | Đưa dữ liệu về như ban đầu |

Các nhóm test:

| File | Kiểm tra |
|---|---|
| `test_basic.py` | Đăng nhập đúng và sai, gọi API khi chưa đăng nhập, thông tin cá nhân, danh sách tài khoản, tra cứu MSSV có và không tồn tại |
| `test_payment_flow.py` | Thanh toán thành công (số dư giảm, học phí thành đã đóng, có trong lịch sử), không trả được học phí đã đóng, không đủ số dư, dùng tài khoản của người khác, OTP sai, OTP hết hạn, gửi lại OTP thì mã cũ mất hiệu lực, xác nhận lại không bị trừ tiền thêm, hủy giao dịch |
| `test_concurrency.py` | 3 giao dịch cùng lúc trên 1 tài khoản thì chỉ 1 thành công và số dư không âm; 3 tài khoản cùng lúc trả 1 khoản học phí thì chỉ 1 thành công, các tài khoản còn lại không mất tiền |

Chạy đúng thì mỗi test hiện `PASSED`, dòng cuối có dạng `18 passed`. Test nào hỏng sẽ hiện `FAILED` kèm dòng kiểm tra bị sai.

Lưu ý: trước mỗi test, dữ liệu bị đưa về như ban đầu (xóa hết giao dịch, OTP, lịch sử biến động số dư, đặt lại số dư và trạng thái học phí). Vì vậy chạy test xong thì lịch sử giao dịch tạo bằng tay trước đó cũng mất.

`npm run db:reset` làm việc reset tương tự nhưng không chạy test. Dùng sau khi test tay trên giao diện, khi tài khoản đã hết tiền hoặc học phí đã đóng hết mà muốn làm lại từ đầu. Lệnh này không xóa người dùng và không cần tắt hệ thống.

## Tắt

```
docker compose down
```

Thêm `-v` nếu muốn xóa luôn database. Database và user chỉ được tạo một lần lúc khởi tạo, nên nếu sửa file trong `backend/sql` hoặc đổi mật khẩu DB trong `.env` thì phải chạy `docker compose down -v` rồi bật lại.
