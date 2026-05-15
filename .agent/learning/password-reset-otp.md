# Password Reset with OTP (Resend Integration)

> Tổng hợp kiến thức về triển khai tính năng quên mật khẩu bằng mã OTP gửi qua dịch vụ Resend trong FastAPI.
> Cập nhật lần cuối: 2026-05-15

---

## Architecture

### Separate Mail Service
- **Ngày**: 2026-05-15
- **Chi tiết**: Tách logic gửi email ra file `mail_service.py` riêng biệt thay vì viết trực tiếp trong router. Điều này giúp dễ dàng thay đổi nhà cung cấp dịch vụ email (SendGrid, Mailgun, SMTP) mà không ảnh hưởng đến logic nghiệp vụ.
- **Files liên quan**: `server/mail_service.py`, `server/routers/auth.py`

---

## How-To

### Quy trình đặt lại mật khẩu bằng OTP
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. **Yêu cầu (Forgot Password)**: Nhận email -> Kiểm tra tồn tại -> Tạo mã 6 số (`random.randint`) -> Lưu vào `User` model kèm `otp_expiry` -> Gửi mail.
  2. **Xác nhận (Reset Password)**: Nhận email, otp, new_password -> So khớp mã và kiểm tra thời gian hết hạn (`datetime.utcnow()`) -> Hash mật khẩu mới (`bcrypt`) -> Xóa mã OTP cũ để tránh dùng lại.
- **Files liên quan**: `server/routers/auth.py`

### Tích hợp Resend API (Free Tier)
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. Cài đặt: `pip install resend`.
  2. Lấy API Key từ resend.com và cấu hình trong `.env`.
  3. Sử dụng `resend.Emails.send()` với template HTML để gửi mail có format đẹp.
- **Files liên quan**: `server/mail_service.py`, `server/.env`

---

## Patterns

### Security: Obfuscating Account Existence
- **Ngày**: 2026-05-15
- **Chi tiết**: Trong API `/forgot-password`, luôn trả về thông báo thành công chung chung (vd: "Nếu email tồn tại, mã sẽ được gửi đi") thay vì báo lỗi "Email không tồn tại". Điều này ngăn chặn kẻ tấn công dò tìm danh sách email người dùng của hệ thống.
- **Files liên quan**: `server/routers/auth.py`
