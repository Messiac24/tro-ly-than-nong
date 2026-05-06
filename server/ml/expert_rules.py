"""
🌿 BỘ LUẬT CHUYÊN GIA NÔNG NGHIỆP (Expert Agricultural Rules)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

File này chứa toàn bộ "Luật Sinh thái Cứng" (Hard Rules) được đúc kết
từ kiến thức nông nghiệp thực tế tại Lâm Đồng.

Mục đích: Bộ lọc BẮT BUỘC chạy TRƯỚC khi Random Forest / XGBoost
đưa ra kết luận, đảm bảo AI không bao giờ "ảo giác" về sinh thái.

Cấu trúc:
  - NHÓM 1: Luật Sinh thái Địa hình (Rủi ro ĐỎ 🔴 / VÀNG 🟡)
    → Kiểm tra tính phù hợp CÂY TRỒNG + VÙNG ĐỊA LÝ
    → Nếu vi phạm → Short-circuit, bẻ lái kết quả ngay lập tức

  - NHÓM 2: Luật Thời tiết Cực đoan (Cảnh báo khẩn cấp)
    → Kiểm tra dữ liệu thời tiết thực tế + loại cây trồng
    → Sinh "Việc cần làm" khẩn cấp (To-do list)

Sử dụng:
  from ml.expert_rules import check_ecology_rules, check_weather_rules
"""

from typing import Optional


# ═══════════════════════════════════════════════════════════════
# NHÓM 1: LUẬT SINH THÁI ĐỊA HÌNH
# ═══════════════════════════════════════════════════════════════
# Các rule "cứng" kiểm tra sự phù hợp giữa CÂY TRỒNG và VÙNG ĐỊA LÝ.
# Nếu vi phạm → trả về dict chứa cảnh báo, AI phải dừng ngay (short-circuit).

# Cấu trúc mỗi rule:
#   - "level": "danger" (🔴) hoặc "warning" (🟡)
#   - "risk_level": 2 (danger) hoặc 1 (warning)
#   - "risk_score": 1.0 (chắc chắn sai) hoặc 0.7-0.8 (rủi ro cao)
#   - "message": Thông điệp ngắn gọn
#   - "reasoning": Giải thích nông nghiệp chi tiết
#   - "suggestion": Khuyến nghị cây thay thế

ECOLOGY_RULES = [
    # ──────────────────────────────────────────────────────────
    # RULE 1: Cà phê Robusta ở vùng cao (> 1000m) → ĐỎ 🔴
    # ──────────────────────────────────────────────────────────
    # Robusta (Coffea canephora) là cây nhiệt đới, cần nhiệt > 20°C,
    # không chịu được lạnh. Ở > 1000m, nhiệt độ thường xuyên < 18°C
    # vào ban đêm, cây sinh trưởng kém, năng suất cực thấp, dễ chết cóng.
    {
        "id": "ROBUSTA_HIGH_ELEVATION",
        "crop": "Cà phê Robusta",
        "condition": lambda elevation, **kw: elevation > 1000,
        "level": "danger",
        "risk_level": 2,
        "risk_score": 1.0,
        "message": (
            "🔴 KHÔNG KHẢ THI – Cà phê Robusta không thể sinh trưởng tốt ở độ cao {elevation}m. "
            "Robusta chỉ thích hợp dưới 800–1000m (vùng nóng ẩm như B'Lao, Di Linh)."
        ),
        "reasoning": (
            "Cà phê Robusta (Coffea canephora) là cây nhiệt đới điển hình, cần nhiệt độ "
            "trung bình 24–30°C và không chịu được lạnh dưới 15°C.\n\n"
            "Ở độ cao {elevation}m (Xuân Trường/Cầu Đất), nhiệt độ ban đêm thường xuyên "
            "xuống dưới 15°C, đặc biệt mùa đông có sương giá. Cây sẽ sinh trưởng cực kỳ kém, "
            "ra hoa thất thường, năng suất giảm 60–80% và có nguy cơ chết cóng cao.\n\n"
            "Tại vùng này bắt buộc phải trồng Cà phê Arabica (Catimor) – giống chè chịu lạnh, "
            "hoặc Chè Ô Long."
        ),
        "suggestion": "Khuyến nghị chuyển đổi sang Cà phê Arabica (Catimor) hoặc Chè Ô Long.",
    },

    # ──────────────────────────────────────────────────────────
    # RULE 2: Sầu riêng Ri6 ở vùng cao (> 1000m) → ĐỎ 🔴
    # ──────────────────────────────────────────────────────────
    # Sầu riêng (Durio zibethinus) là cây nhiệt đới, cần nhiệt > 22°C,
    # không chịu được gió mạnh và nhiệt độ < 15°C.
    {
        "id": "DURIAN_HIGH_ELEVATION",
        "crop": "Sầu riêng Ri6",
        "condition": lambda elevation, **kw: elevation > 1000,
        "level": "danger",
        "risk_level": 2,
        "risk_score": 1.0,
        "message": (
            "🔴 KHÔNG KHẢ THI – Sầu riêng Ri6 không thể sống ở độ cao {elevation}m. "
            "Sầu riêng là cây nhiệt đới, chỉ trồng được ở vùng nóng (< 800m)."
        ),
        "reasoning": (
            "Sầu riêng (Durio zibethinus) là cây nhiệt đới không chịu lạnh, yêu cầu "
            "nhiệt độ trung bình 24–32°C quanh năm.\n\n"
            "Ở độ cao {elevation}m, nhiệt độ thường xuyên dưới 20°C và có thể xuống "
            "dưới 10°C vào mùa đông. Cây sẽ rụng sạch lá, ngừng sinh trưởng hoàn toàn "
            "và chết cóng.\n\n"
            "Ngoài ra, gió mạnh ở vùng cao sẽ gãy cành và rụng trái hàng loạt. "
            "Rủi ro mất trắng 100% vốn đầu tư."
        ),
        "suggestion": "Khuyến nghị chuyển sang Cà phê Arabica hoặc Chè Ô Long tại vùng này.",
    },

    # ──────────────────────────────────────────────────────────
    # RULE 3: Cà phê Arabica ở vùng thấp (< 800m) → VÀNG/ĐỎ 🟡🔴
    # ──────────────────────────────────────────────────────────
    # Arabica (Coffea arabica) ưa khí hậu mát, 15–24°C, độ cao > 1000m.
    # Trồng ở vùng nóng < 800m: kiệt sức, bệnh Rỉ sắt bùng phát.
    {
        "id": "ARABICA_LOW_ELEVATION",
        "crop": "Cà phê Arabica",
        "condition": lambda elevation, **kw: elevation < 1000,
        "level": "danger",
        "risk_level": 2,
        "risk_score": 0.85,
        "message": (
            "🔴 RỦI RO BỆNH HẠI CAO – Cà phê Arabica không phù hợp ở độ cao {elevation}m. "
            "Arabica cần khí hậu lạnh, độ cao > 1000m (như Cầu Đất, Xuân Trường)."
        ),
        "reasoning": (
            "Cà phê Arabica (Coffea arabica) là giống ưa lạnh, sinh thái lý tưởng ở "
            "1000–1500m với nhiệt độ 15–24°C.\n\n"
            "Trồng ở {elevation}m (B'Lao) nhiệt độ trung bình 25–30°C sẽ khiến cây "
            "kiệt sức, ra hoa thất thường, chất lượng hạt kém (mất hương vị đặc trưng).\n\n"
            "Đặc biệt, ở vùng nóng ẩm Arabica cực kỳ dễ bùng phát bệnh Rỉ sắt "
            "(Hemileia vastatrix) – bệnh nấm chết cành, có thể phá hủy 30–50% vườn "
            "cà phê trong 1 mùa."
        ),
        "suggestion": "Khuyến nghị chuyển sang Cà phê Robusta – giống chịu nóng, kháng bệnh tốt.",
    },

    # ──────────────────────────────────────────────────────────
    # RULE 4: Chè Ô Long ở vùng thấp nóng (< 1000m) → VÀNG 🟡
    # ──────────────────────────────────────────────────────────
    # Chè Ô Long cao cấp đòi hỏi biên độ nhiệt ngày/đêm lớn, sương mù,
    # khí hậu mát mẻ (16–22°C). Trồng ở vùng nóng: mất hương vị, 
    # chỉ bán được giá chè xanh thường.
    {
        "id": "OOLONG_LOW_ELEVATION",
        "crop": "Chè Ô Long",
        "condition": lambda elevation, **kw: elevation < 1000,
        "level": "warning",
        "risk_level": 1,
        "risk_score": 0.70,
        "message": (
            "🟡 CẢNH BÁO CHẤT LƯỢNG THƯƠNG MẠI – Chè Ô Long trồng ở {elevation}m "
            "sẽ mất hoàn toàn hương vị Ô Long đặc trưng."
        ),
        "reasoning": (
            "Chè Ô Long (Oolong) là giống chè cao cấp đòi hỏi biên độ nhiệt ngày/đêm lớn "
            "(> 10°C) và sương mù thường xuyên (như Xuân Trường, Cầu Đất ở 1500m) để búp chè "
            "tích lũy hương vị đặc trưng.\n\n"
            "Trồng ở {elevation}m (B'Lao, nóng ẩm), búp chè lớn quá nhanh, lá mỏng, "
            "mất hoàn toàn hương Ô Long đặc trưng.\n\n"
            "Sản phẩm chỉ bán được giá chè xanh thông thường (giảm 60–70% giá trị), "
            "dẫn đến phá vỡ hoàn toàn bài toán tài chính đã tính ở trên."
        ),
        "suggestion": "Nên trồng Chè Ô Long tại vùng cao > 1200m. Tại B'Lao, khuyến nghị trồng Cà phê Robusta hoặc Sầu riêng Ri6.",
    },
]


def check_ecology_rules(crop_name: str, elevation: int, location_name: str = "") -> Optional[dict]:
    """
    Kiểm tra tất cả Luật Sinh thái Địa hình.
    
    Hàm này chạy TRƯỚC khi Random Forest / XGBoost đưa ra kết luận.
    Nếu phát hiện vi phạm → trả về dict cảnh báo (short-circuit).
    Nếu không vi phạm → trả về None (cho phép AI tiếp tục phân tích).
    
    Args:
        crop_name: Tên cây trồng (e.g., "Cà phê Robusta")
        elevation: Độ cao vùng trồng (mét)
        location_name: Tên vùng (e.g., "Phường Xuân Trường")
    
    Returns:
        dict chứa cảnh báo nếu vi phạm, None nếu an toàn.
    """
    for rule in ECOLOGY_RULES:
        if rule["crop"] != crop_name:
            continue
        
        if rule["condition"](elevation=elevation):
            # Format message với thông tin thực tế
            formatted_message = rule["message"].format(
                elevation=elevation,
                location=location_name
            )
            formatted_reasoning = rule["reasoning"].format(
                elevation=elevation,
                location=location_name
            )
            
            return {
                "rule_id": rule["id"],
                "level": rule["level"],
                "risk_level": rule["risk_level"],
                "risk_score": rule["risk_score"],
                "message": formatted_message,
                "reasoning": formatted_reasoning,
                "suggestion": rule["suggestion"],
            }
    
    return None  # Không vi phạm rule nào → an toàn


# ═══════════════════════════════════════════════════════════════
# NHÓM 2: LUẬT THỜI TIẾT CỰC ĐOAN
# ═══════════════════════════════════════════════════════════════
# Sinh ra "Việc cần làm" khẩn cấp dựa trên dữ liệu thời tiết + cây trồng.
# Các rule này KHÔNG short-circuit, chỉ bổ sung cảnh báo vào checklist.

WEATHER_RULES = [
    # ──────────────────────────────────────────────────────────
    # RULE 4: Sương muối (Đặc sản Xuân Trường)
    # ──────────────────────────────────────────────────────────
    # Sương muối xảy ra khi temp_min < 6°C, phá hủy lá non và búp chè.
    {
        "id": "FROST_WARNING",
        "crops": ["Cà phê Arabica", "Chè Ô Long"],
        "condition": lambda temp_min, elevation, **kw: temp_min < 6.0 and elevation > 1000,
        "level": "danger",
        "title": "🔴 CẢNH BÁO SƯƠNG MUỐI KHẨN CẤP",
        "description": (
            "Nhiệt độ cực tiểu {temp_min}°C – nguy cơ sương muối rất cao tại vùng cao {elevation}m. "
            "Sương muối sẽ đốt cháy lá non, búp chè và chồi cà phê non."
        ),
        "actions": [
            {"action": "🔥 Hun khói: Đốt rác/cỏ ẩm ở đầu hướng gió vào 3–5h sáng để tạo màng khói giữ ấm", "done": False},
            {"action": "💧 Bơm nước tưới rửa sương ngay lúc sáng sớm TRƯỚC khi mặt trời lên (cứu cháy lá)", "done": False},
            {"action": "🧊 Tủ gốc bằng rơm/cỏ khô dày 10–15cm để giữ ấm bộ rễ", "done": False},
            {"action": "🛡️ Che phủ bạt cho cây non dưới 2 tuổi", "done": False},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # RULE 5: Nấm rễ Sầu riêng (Đặc sản mùa mưa B'Lao)
    # ──────────────────────────────────────────────────────────
    # Mưa lớn > 50mm/ngày trong nhiều ngày → úng rễ → nấm Phytophthora.
    {
        "id": "DURIAN_ROOT_ROT",
        "crops": ["Sầu riêng Ri6"],
        "condition": lambda precipitation, **kw: precipitation > 50.0,
        "level": "warning",
        "title": "🟡 NGUY CƠ ÚNG RỄ VÀ NẤM PHYTOPHTHORA",
        "description": (
            "Lượng mưa {precipitation}mm cao bất thường – nguy cơ úng rễ và bùng phát "
            "nấm Phytophthora palmivora ở gốc sầu riêng."
        ),
        "actions": [
            {"action": "🚫 TUYỆT ĐỐI ngưng bón phân Đạm (Ure) – rễ đang yếu không hấp thụ được", "done": False},
            {"action": "🔧 Lập tức khơi thông mương rãnh thoát nước xung quanh gốc", "done": False},
            {"action": "💊 Chuẩn bị thuốc trị nấm gốc Đồng (Aliette 80WG hoặc Ridomil Gold) để quét gốc/tưới rễ", "done": False},
            {"action": "👀 Kiểm tra gốc cây: nếu vỏ gốc bị thối nâu/đen, ướt nhầy → xử lý ngay", "done": False},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # RULE 6: Hạn hán & Bón phân Robusta
    # ──────────────────────────────────────────────────────────
    # Nhiệt > 32°C, mưa = 0 → phân hóa học bốc hơi, rễ không hấp thụ.
    {
        "id": "DROUGHT_FERTILIZER_WARNING",
        "crops": ["Cà phê Robusta"],
        "condition": lambda temp_max, precipitation, **kw: temp_max > 32.0 and precipitation < 5.0,
        "level": "warning",
        "title": "🟡 KHUYẾN CÁO DINH DƯỠNG – NẮNG NÓNG KÉO DÀI",
        "description": (
            "Nhiệt độ cao {temp_max}°C và lượng mưa chỉ {precipitation}mm – "
            "điều kiện nắng nóng khô hạn."
        ),
        "actions": [
            {"action": "🚫 TUYỆT ĐỐI không rải phân hóa học (NPK, Ure) trên mặt đất – phân sẽ bốc hơi do nắng nóng, rễ không hấp thụ được", "done": False},
            {"action": "💧 Cần tưới đẫm nước TRƯỚC khi bón phân, hoặc chuyển sang sử dụng phân bón lá", "done": False},
            {"action": "🌿 Tủ gốc bằng cỏ khô/rơm để giữ ẩm đất", "done": False},
            {"action": "⏰ Tưới nước vào sáng sớm (5–7h) hoặc chiều muộn (17–18h), tránh tưới giữa trưa", "done": False},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # RULE 7: Mưa lớn + Arabica ở vùng cao → Rỉ sắt
    # ──────────────────────────────────────────────────────────
    # Mưa nhiều + ẩm cao → bệnh rỉ sắt (Hemileia vastatrix) bùng phát.
    {
        "id": "ARABICA_RUST_WARNING",
        "crops": ["Cà phê Arabica"],
        "condition": lambda precipitation, **kw: precipitation > 100.0,
        "level": "warning",
        "title": "🟡 NGUY CƠ BỆNH RỈ SẮT ARABICA",
        "description": (
            "Lượng mưa {precipitation}mm – độ ẩm cao kéo dài tạo điều kiện "
            "cho nấm Rỉ sắt (Hemileia vastatrix) bùng phát trên lá cà phê Arabica."
        ),
        "actions": [
            {"action": "💊 Phun thuốc gốc Đồng (Copper Hydroxide, Bordeaux) phòng rỉ sắt ngay", "done": False},
            {"action": "✂️ Tỉa cành tạo thông thoáng, giảm độ ẩm tán lá", "done": False},
            {"action": "👀 Kiểm tra mặt dưới lá: nếu thấy bột vàng cam → rỉ sắt đã xuất hiện", "done": False},
        ],
    },

    # ──────────────────────────────────────────────────────────
    # RULE 8: Lạnh sâu + Sầu riêng → Cảnh báo
    # ──────────────────────────────────────────────────────────
    {
        "id": "DURIAN_COLD_STRESS",
        "crops": ["Sầu riêng Ri6"],
        "condition": lambda temp_min, **kw: temp_min < 15.0,
        "level": "warning",
        "title": "🟡 SẦU RIÊNG STRESS LẠNH",
        "description": (
            "Nhiệt độ cực tiểu {temp_min}°C – sầu riêng bắt đầu stress lạnh, "
            "ảnh hưởng ra hoa đậu trái."
        ),
        "actions": [
            {"action": "🧊 Tủ gốc giữ ấm bộ rễ, tưới nước ấm vào sáng sớm", "done": False},
            {"action": "🌿 Phun phân bón lá Kali (K₂SO₄) tăng sức đề kháng", "done": False},
            {"action": "⏸️ Tạm ngưng bón phân gốc cho đến khi nhiệt độ ổn định > 20°C", "done": False},
        ],
    },
]


def check_weather_rules(
    crop_name: str,
    temp_max: float,
    temp_min: float,
    precipitation: float,
    elevation: int = 0,
) -> list[dict]:
    """
    Kiểm tra tất cả Luật Thời tiết Cực đoan.
    
    Hàm này chạy SAU khi check_ecology_rules đã xác nhận cây trồng
    phù hợp với vùng. Sinh ra danh sách "Việc cần làm" khẩn cấp.
    
    Args:
        crop_name: Tên cây trồng
        temp_max: Nhiệt độ cực đại (°C)
        temp_min: Nhiệt độ cực tiểu (°C)
        precipitation: Lượng mưa (mm/ngày)
        elevation: Độ cao (mét)
    
    Returns:
        list[dict] chứa các cảnh báo thời tiết + actions.
        Rỗng nếu không có cảnh báo nào.
    """
    warnings = []
    
    for rule in WEATHER_RULES:
        if crop_name not in rule["crops"]:
            continue
        
        if rule["condition"](
            temp_max=temp_max,
            temp_min=temp_min,
            precipitation=precipitation,
            elevation=elevation,
        ):
            formatted_title = rule["title"]
            formatted_desc = rule["description"].format(
                temp_max=temp_max,
                temp_min=temp_min,
                precipitation=precipitation,
                elevation=elevation,
            )
            
            warnings.append({
                "rule_id": rule["id"],
                "level": rule["level"],
                "title": formatted_title,
                "description": formatted_desc,
                "actions": rule["actions"],
            })
    
    return warnings


# ═══════════════════════════════════════════════════════════════
# TIỆN ÍCH: Tổng hợp kết quả Expert Rules
# ═══════════════════════════════════════════════════════════════

def run_expert_check(
    crop_name: str,
    location_name: str,
    elevation: int,
    temp_max: float,
    temp_min: float,
    precipitation: float,
) -> dict:
    """
    Chạy toàn bộ bộ luật chuyên gia (Sinh thái + Thời tiết).
    
    Đây là hàm entry-point chính, gọi từ router predict.
    
    Returns:
        {
            "ecology_violation": dict | None,   # Vi phạm sinh thái (nếu có)
            "weather_warnings": list[dict],      # Cảnh báo thời tiết
            "has_critical_issue": bool,           # True nếu có vi phạm sinh thái
        }
    """
    ecology = check_ecology_rules(crop_name, elevation, location_name)
    weather = check_weather_rules(crop_name, temp_max, temp_min, precipitation, elevation)
    
    return {
        "ecology_violation": ecology,
        "weather_warnings": weather,
        "has_critical_issue": ecology is not None and ecology.get("risk_level", 0) == 2,
    }
