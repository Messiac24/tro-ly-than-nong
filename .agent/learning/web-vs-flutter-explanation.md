# Tại sao Flutter lại khác hoàn toàn bản Web?

Chào bạn, đây là bản giải thích nhanh kiểu "coffee talk" về việc tại sao chúng ta lại có hai bộ code khác nhau cho cùng một ứng dụng.

## 1. Web là "Tài liệu", Flutter là "Bản vẽ"

- **Web (HTML/CSS):** Hoạt động theo cơ chế **DOM**. Bạn định nghĩa các thẻ tài liệu (h1, div, p) và trình duyệt sẽ sắp xếp chúng.
- **Flutter (Dart):** Hoạt động theo cơ chế **Widget**. Flutter coi mọi thứ là một bản vẽ. Nó không hỏi trình duyệt "Nút bấm trông thế nào?", mà nó tự cầm cọ vẽ cái nút bấm đó lên từng pixel của màn hình.

## 2. So sánh trực quan (Dành cho Dev)

| Đặc điểm      | Bản Web (hiện tại)                     | Bản Flutter (vừa cập nhật)                                |
| :------------ | :------------------------------------- | :-------------------------------------------------------- |
| **Giao diện** | HTML tags (`<div>`, `<section>`)       | Widgets (`Container`, `Column`)                           |
| **Định dạng** | CSS (`.card { border-radius: 20px; }`) | BoxDecoration (`borderRadius: BorderRadius.circular(20)`) |
| **Tương tác** | Event Listeners (JS `onclick`)         | Callbacks (`onPressed: () => {}`)                         |
| **Dàn trang** | Flexbox / Grid                         | Flex (Row/Column) / Slivers                               |

## 3. Quy trình "Porting" (Chuyển đổi) tôi đã thực hiện

Khi bạn thấy tôi sửa `main.dart`, thực chất tôi đang thực hiện các bước:

1. **Trích xuất Design Tokens:** Lấy mã màu `#2D6A4F`, font-size, độ mờ shadow từ file `style.css`.
2. **Tái cấu trúc Layout:** Chuyển cấu trúc `form-panel` bên trái và `dashboard-panel` bên phải của Web sang `AnalysisPage` và `DashboardPage` dạng các Tab trên Mobile.
3. **Áp dụng "Premium Backbone":** Đảm bảo các nguyên tắc về Glassmorphism và spacing 8px được giữ nguyên dù ngôn ngữ code thay đổi.

## 4. Lợi ích sau này

Dù bây giờ bạn thấy lạ lẫm, nhưng file `main.dart` này chính là **"Một cho tất cả"**. Bạn có thể dùng chính code này để:

- Build file `.apk` / `.aab` cho Android.
- Build file `.ipa` cho iPhone.
- Và thậm chí build lại thành một bản Web mới thay thế cho bản HTML/JS cũ nếu bạn muốn đồng nhất 100% code.
