# Agricultural Logic (Expert Rules & Decision Engine)

> Tổng hợp kiến thức về logic nghiệp vụ nông nghiệp, quy tắc chuyên gia và công cụ tính toán ROI trong dự án.
> Cập nhật lần cuối: 2026-05-15

---

## Architecture

### Expert Rules Engine (Short-circuit Pattern)
- **Ngày**: 2026-05-15
- **Chi tiết**: Hệ thống sử dụng bộ quy tắc "cứng" (Hard Rules) để kiểm tra tính phù hợp sinh thái trước khi chạy các mô hình AI. Nếu vi phạm nghiêm trọng (ví dụ: trồng Robusta ở độ cao > 1000m), hệ thống sẽ ngắt (short-circuit) và trả về cảnh báo nguy hiểm ngay lập tức.
- **Files liên quan**: `server/ml/expert_rules.py`

### Decision Engine & ROI Simulation
- **Ngày**: 2026-05-15
- **Chi tiết**: Tính toán tài chính dựa trên 2 chế độ: "Kiến thiết" (đầu tư mới, tính khấu hao CAPEX và năng suất tăng dần theo 5-7 năm) và "Kinh doanh" (duy trì, tính ROI hàng năm). Engine tích hợp "Hệ số trừng phạt giá" nếu cây trồng bị trồng sai vùng sinh thái nhưng chưa đến mức báo tử.
- **Files liên quan**: `server/ml/decision_engine.py`

---

## How-To

### Cách tính Năng suất thực tế (Estimated Yield)
- **Ngày**: 2026-05-15
- **Bước thực hiện**:
  1. Lấy năng suất nền (Baseline) từ `CROP_MAPPING`.
  2. Kiểm tra điều kiện thời tiết cực đoan (Sương muối, mưa lớn).
  3. Áp dụng các hình phạt năng suất (Yield Penalties) theo tỷ lệ phần trăm.
  4. Công thức: `Final_Yield = Baseline * (1 - P_frost) * (1 - P_rain)`.
- **Files liên quan**: `server/ml/decision_engine.py`

---

## Patterns

### Price Penalty Pattern
- **Ngày**: 2026-05-15
- **Chi tiết**: Mô hình hóa việc giảm giá trị thương mại của nông sản khi chất lượng bị ảnh hưởng bởi môi trường. Ví dụ: Chè Ô Long trồng vùng thấp nóng sẽ bị giáng cấp xuống "chè xanh thường" và áp dụng hệ số giá 0.2 (giảm 80% giá trị).
- **Files liên quan**: `server/ml/decision_engine.py`
