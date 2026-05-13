# Flutter Premium UI

> Tổng hợp kiến thức về việc xây dựng giao diện Flutter cao cấp (Premium) và đồng bộ thiết kế từ nền tảng Web.
> Cập nhật lần cuối: 2026-05-13

---

## Architecture

### Cơ chế vẽ (Rendering Engine) vs Web DOM
- **Ngày**: 2026-05-13
- **Chi tiết**: Flutter không sử dụng DOM của trình duyệt mà tự vẽ mọi thứ lên màn hình bằng engine riêng. Do đó, không thể dùng trực tiếp HTML/CSS mà phải "dịch" các design tokens (color, shadow, spacing) sang hệ thống Widget của Flutter.
- **Files liên quan**: `lib/main.dart`, `client/style.css`

---

## Bugs & Solutions

### Sai sót trong cấu hình `pubspec.yaml`
- **Ngày**: 2026-05-13
- **Vấn đề**: Lỗi `No pubspec.yaml file found` hoặc lỗi import package khi tên project trong file config không khớp với tên thư mục.
- **Root cause**: Tên project bị viết sai chính tả (`fluter_nongsan`) và chạy lệnh từ thư mục gốc thay vì thư mục project.
- **Fix**: Sửa lại thuộc tính `name` trong `pubspec.yaml` cho đúng và luôn dùng lệnh `cd` vào thư mục project trước khi `flutter run`.
- **Files liên quan**: `flutter_nongsan/pubspec.yaml`

### Lỗi Deprecated `withOpacity` trên Flutter mới
- **Ngày**: 2026-05-13
- **Vấn đề**: Cảnh báo lint khi dùng `.withOpacity(x)` trên các bản Flutter SDK 3.11+.
- **Root cause**: Flutter đã giới thiệu phương thức mới để tránh mất độ chính xác màu.
- **Fix**: Thay thế bằng `.withValues(alpha: x)`.
- **Files liên quan**: `lib/main.dart`

---

## How-To

### Đồng bộ thiết kế Premium từ Web sang Flutter
- **Ngày**: 2026-05-13
- **Bước thực hiện**:
  1. Trích xuất bảng màu (Primary, Secondary, Surface) và Google Fonts từ `style.css`.
  2. Áp dụng `ThemeData` toàn cục để giữ tính nhất quán.
  3. Sử dụng `BoxShadow` với màu mờ (`withValues`) và `borderRadius` lớn (24-30px) để tạo cảm giác Premium.
  4. Thiết kế thanh điều hướng dạng floating sử dụng `ClipRRect` kết hợp `BoxShadow` bên ngoài.
- **Files liên quan**: `lib/main.dart`, `client/style.css`

---

## Patterns

### Glassmorphism trong Flutter
- **Ngày**: 2026-05-13
- **Chi tiết**: Sử dụng Container với màu trắng đục (`withValues(alpha: 0.8)`) kết hợp với `BoxShadow` mờ để giả lập hiệu ứng kính trên nền ứng dụng.
- **Ví dụ code**:
  ```dart
  Container(
    decoration: BoxDecoration(
      color: Colors.white.withValues(alpha: 0.8),
      borderRadius: BorderRadius.circular(30),
      boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 20)],
    ),
  )
  ```
- **Files liên quan**: `lib/main.dart`
