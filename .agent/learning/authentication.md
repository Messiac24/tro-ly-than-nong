# Authentication & Security

> Tổng hợp kiến thức về hệ thống xác thực, gửi mã OTP và bảo mật tài khoản người dùng.
> Cập nhật lần cuối: 2026-05-15

---

## Architecture

### Gmail SMTP Integration for OTP
- **Ngày**: 2026-05-15
- **Chi tiết**: Thay thế các dịch vụ gửi mail bên thứ ba bằng Gmail SMTP (`smtplib`) sử dụng Google App Password. Giải pháp này giúp gửi OTP ổn định mà không cần xác thực tên miền phức tạp trong giai đoạn phát triển.
- **Files liên quan**: `server/mail_service.py`, `server/.env`

---

## Bugs & Solutions

### Case Sensitivity in Email Search
- **Ngày**: 2026-05-15
- **Vấn đề**: Người dùng không thể reset mật khẩu nếu nhập email có ký tự hoa (ví dụ: User@gmail.com) trong khi DB lưu chữ thường.
- **Root cause**: So sánh chuỗi trong SQLite mặc định có phân biệt hoa thường.
- **Fix**: Sử dụng hàm `.lower()` cho email trước khi lưu vào Database và trước khi thực hiện truy vấn tìm kiếm.
- **Files liên quan**: `server/routers/auth.py`

---

## How-To

### Cách thiết lập Rate Limiting cho gửi OTP
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. Tạo bảng hoặc dict lưu trữ `last_sent_time` và `attempt_count` cho mỗi email.
  2. Kiểm tra thời gian chênh lệch giữa các lần yêu cầu (ví dụ: tối thiểu 60s giữa 2 lần gửi).
  3. Giới hạn số lần yêu cầu tối đa trong một khoảng thời gian (ví dụ: 3 lần/10 phút) để chống spam.
- **Files liên quan**: `server/routers/auth.py`

---

## Patterns

### Password Hashing Convention
- **Ngày**: 2026-05-15
- **Chi tiết**: Luôn sử dụng `bcrypt` để hash mật khẩu trước khi lưu. Tuyệt đối không lưu mật khẩu dạng plain text hoặc mã hóa 2 chiều (reversible encryption).
- **Files liên quan**: `server/routers/auth.py`
