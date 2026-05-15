# Frontend Design

> Tổng hợp kiến thức về hệ thống thiết kế Organic Refined (Nông nghiệp Tinh tế) và các tiêu chuẩn UI/UX cao cấp trong dự án.
> Cập nhật lần cuối: 2026-05-15

---

## Architecture

### Aesthetic Direction: Organic Refined
- **Ngày**: 2026-05-15
- **Chi tiết**: Quyết định sử dụng phong cách "Organic Refined" – giao thoa giữa thiên nhiên (Earth tones, Deep Forest Green) và công nghệ cao (Glassmorphism, Precise Typography). Mục tiêu là tạo sự tin cậy nhưng vẫn gần gũi với nông dân Lâm Đồng.
- **Files liên quan**: `client/style.css`, `client/index.html`

### Layered Depth System
- **Ngày**: 2026-05-15
- **Chi tiết**: Sử dụng hệ thống đổ bóng đa lớp (Layered Shadows) kết hợp với Glassmorphism (backdrop-filter: blur(24px)) để tạo chiều sâu mà không làm nặng giao diện. Nền sử dụng Mesh Gradient "Sunrise" và Noise Texture (0.04 opacity) để giảm cảm giác "phẳng" của kỹ thuật số.
- **Files liên quan**: `client/style.css`

---

## Bugs & Solutions

### Class Mismatch in Authentication Modals
- **Ngày**: 2026-05-15
- **Vấn đề**: Modal đổi mật khẩu không nhận đúng style bo góc và shadow.
- **Root cause**: Trong HTML dùng class `.auth-container` nhưng trong CSS lại định nghĩa là `.auth-card`.
- **Fix**: Chuẩn hóa toàn bộ container của modal về class `.auth-card` để đồng bộ với Design System.
- **Files liên quan**: `client/index.html`, `client/style.css`

---

## How-To

### Cách tạo một Dropdown Menu chuẩn "Luxury"
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. Sử dụng `background: rgba(255, 255, 255, 0.75)` kết hợp `backdrop-filter: blur(24px) saturate(180%)`.
  2. Thêm viền mảnh `1px solid rgba(255, 255, 255, 0.4)` để tạo hiệu ứng khối kính.
  3. Sử dụng `Plus Jakarta Sans` cho Header và `Be Vietnam Pro` cho nội dung.
  4. Thêm hiệu ứng hover `padding-left` tăng dần kết hợp đổi màu icon sang `--color-accent` (vàng nắng).
- **Files liên quan**: `client/style.css`, `client/index.html`

---

## Patterns

### Design Tokens Pattern
- **Ngày**: 2026-05-15
- **Chi tiết**: Toàn bộ hệ thống màu sắc và khoảng cách phải được quản lý qua CSS Variables trong `:root`. Không hardcode màu trong các component lẻ.
- **Ví dụ code**:
  ```css
  :root {
      --color-primary: #1B4332; /* Deep Forest */
      --color-accent: #fca311;  /* Sunrise Saffron */
      --shadow-xl: 0 24px 48px rgba(27, 67, 50, 0.15);
  }
  ```
- **Files liên quan**: `client/style.css`
