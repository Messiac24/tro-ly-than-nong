"""
⚙️ Cấu hình Hệ thống - Hằng số & Ánh xạ

Chứa toàn bộ hằng số hệ thống, ánh xạ vùng canh tác,
thông tin cây trồng, và các ngưỡng rủi ro.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── API Key ─────────────────────────────────────────────────
API_KEY = os.getenv("API_KEY", "dev-key-ai-nong-san-2026")

# ── Ánh xạ Vùng Canh Tác ───────────────────────────────────
# Dữ liệu thực tế: Tọa độ GPS, độ cao, tên tìm kiếm
LOCATION_MAPPING = {
    "Phường B'Lao": {
        "display_name": "Phường B'Lao – TP. Bảo Lộc, Lâm Đồng",
        "search_keywords": [
            "Phường B'Lao", "Phường Lộc Sơn",
            "Xã Lộc Nga", "Bảo Lộc"
        ],
        "coordinates": {"lat": 11.5247, "lon": 107.859},
        "elevation": 800,  # mét
        "climate": "Mưa nhiều, nhiệt đới gió mùa",
        "suitable_crops": ["Cà phê Robusta", "Sầu riêng Ri6", "Mắc ca"],
    },
    "Phường Xuân Trường": {
        "display_name": "Phường Xuân Trường – TP. Đà Lạt, Lâm Đồng",
        "search_keywords": [
            "Xã Trạm Hành", "Xã Xuân Thọ",
            "Cầu Đất", "Đà Lạt"
        ],
        "coordinates": {"lat": 11.89, "lon": 108.54},
        "elevation": 1500,  # mét
        "climate": "Sương giá, khí hậu ôn đới núi cao",
        "suitable_crops": ["Cà phê Arabica", "Chè Ô Long", "Hồng giòn"],
    },
}

# ── Ánh xạ Cây Trồng ───────────────────────────────────────
CROP_MAPPING = {
    "Cà phê Robusta": {
        "variety": "TR4, TR9",
        "icon": "☕",
        "price_source": "yahoo_finance",
        "yahoo_ticker": "RC=F",  # Robusta Coffee Futures
        "model_type": "tft",
        "baseline_yield_ton_per_ha": 3.5,
        "cost_ratio": 0.65,  # 65% vốn là chi phí
        "description": "Phổ biến nhất tại B'Lao, chiếm >90% diện tích",
    },
    "Cà phê Arabica": {
        "variety": "Catimor",
        "icon": "☕",
        "price_source": "yahoo_finance",
        "yahoo_ticker": "KC=F",  # Arabica Coffee Futures
        "model_type": "tft",
        "baseline_yield_ton_per_ha": 2.5,
        "cost_ratio": 0.70,
        "description": "Phổ biến tại Cầu Đất – Đà Lạt",
    },
    "Sầu riêng Ri6": {
        "variety": "Ri6",
        "icon": "🍈",
        "price_source": "synthetic_csv",
        "csv_file": "raw_durian_ri6.csv",
        "model_type": "xgboost",
        "baseline_yield_ton_per_ha": 18.0,
        "cost_ratio": 0.55,
        "description": "Phổ biến nhất Lâm Đồng, giá biến động mạnh theo mùa",
        "harvest_months": [6, 7, 8],  # Mùa thu hoạch chính
    },
    "Chè Ô Long": {
        "variety": "Ô Long (Oolong)",
        "icon": "🍵",
        "price_source": "synthetic_csv",
        "csv_file": "raw_oolong.csv",
        "model_type": "xgboost",
        "baseline_yield_ton_per_ha": 12.0,
        "cost_ratio": 0.60,
        "description": "Đặc sản Cầu Đất – Đà Lạt, giá trị cao",
        "harvest_months": list(range(1, 13)),  # Thu hoạch rải rác quanh năm
    },
}

# ── Gợi ý Cây thay thế theo Vùng Sinh Thái ─────────────────
# Khi risk_level == 2, hệ thống sẽ gợi ý cây từ bảng này
# (tự động loại bỏ cây đang bị từ chối)
CROP_ALTERNATIVES = {
    "Phường B'Lao": ["Cà phê Robusta", "Sầu riêng Ri6", "Mắc ca"],
    "Phường Xuân Trường": ["Cà phê Arabica", "Chè Ô Long", "Hồng giòn"],
}

# ── Ngưỡng Rủi ro (Pseudo-Labeling Rules) ──────────────────
# Dùng cho Feature Engineering và Random Forest Classifier
RISK_THRESHOLDS = {
    # Mức 2 (Nguy hiểm) - Dừng ngay, TỪ CHỐI canh tác
    "durian_max_elevation": 1400,      # Sầu riêng không sống > 1400m
    "frost_temp_celsius": 5.0,         # Nhiệt độ < 5°C → sương muối
    "heavy_rain_mm_per_week": 200,     # Mưa > 200mm/tuần → ngập

    # Mức 1 (Chú ý) - Cảnh báo, cần theo dõi
    "cold_temp_celsius": 10.0,         # Nhiệt 5–10°C → lạnh sâu
    "moderate_rain_mm_per_week": 100,  # Mưa 100–200mm → cần khơi rãnh
}

# ── Công thức Sụt giảm Năng suất ────────────────────────────
# Final_Yield = Baseline * (1 - penalty_frost) * (1 - penalty_rain)
YIELD_PENALTIES = {
    "frost_below_5c": 0.40,     # Giảm 40% năng suất khi sương muối
    "cold_5_to_10c": 0.15,      # Giảm 15% năng suất khi lạnh sâu
    "heavy_rain_200mm": 0.30,   # Giảm 30% năng suất khi mưa lớn
}

# ── Checklist Hành động (Rule-based, Hardcoded) ─────────────
# Sinh ra dựa trên điều kiện thời tiết, không dùng LLM
ACTION_CHECKLIST = {
    "heavy_rain": [
        {"action": "Khơi thông rãnh thoát nước", "done": False},
        {"action": "Phun thuốc phòng nấm rễ", "done": False},
        {"action": "Kiểm tra hệ thống thoát nước quanh gốc", "done": False},
    ],
    "frost": [
        {"action": "Tủ gốc giữ ấm bằng rơm/cỏ khô", "done": False},
        {"action": "Phun sương rửa lá vào sáng sớm", "done": False},
        {"action": "Che phủ bạt cho cây non", "done": False},
    ],
    "cold": [
        {"action": "Theo dõi nhiệt độ hàng ngày", "done": False},
        {"action": "Tăng cường bón kali để tăng sức đề kháng", "done": False},
    ],
    "normal": [
        {"action": "Bón phân theo lịch mùa vụ", "done": False},
        {"action": "Kiểm tra độ ẩm đất", "done": False},
        {"action": "Theo dõi sâu bệnh định kỳ", "done": False},
    ],
}

# ── Open-Meteo API Config ──────────────────────────────────
OPEN_METEO_BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
WEATHER_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "relative_humidity_2m_max",
    "wind_speed_10m_max",
]
