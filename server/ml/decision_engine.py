import os
import sys

# Thêm thư mục server vào sys.path để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CROP_MAPPING, YIELD_PENALTIES, ACTION_CHECKLIST

# ── Thời gian kiến thiết & trưởng thành của từng loại cây ──
# capex_years: Số năm đầu tư ban đầu (chưa có thu hoạch)
# full_yield_year: Năm bắt đầu cho năng suất 100%
# capex_multiplier: Hệ số chi phí CAPEX so với chi phí duy trì hàng năm
# yield_ramp: Tỷ lệ năng suất từng năm sau capex (0→100%)
CROP_MATURITY_YEARS = {
    "Cà phê Robusta": {
        "capex_years": 3, "full_yield_year": 5, "capex_multiplier": 2.0,
        "yield_ramp": [0, 0, 0, 0.30, 0.60, 1.0],  # Năm 0-2: 0%, Năm 3: 30%, Năm 4: 60%, Năm 5: 100%
    },
    "Cà phê Arabica": {
        "capex_years": 3, "full_yield_year": 5, "capex_multiplier": 2.2,
        "yield_ramp": [0, 0, 0, 0.25, 0.55, 1.0],
    },
    "Chè Ô Long": {
        "capex_years": 2, "full_yield_year": 4, "capex_multiplier": 2.5,
        "yield_ramp": [0, 0, 0.30, 0.65, 1.0],  # Năm 0-1: 0%, Năm 2: 30%, Năm 3: 65%, Năm 4: 100%
    },
    "Sầu riêng Ri6": {
        "capex_years": 5, "full_yield_year": 7, "capex_multiplier": 1.8,
        "yield_ramp": [0, 0, 0, 0, 0, 0.20, 0.50, 1.0],  # Năm 0-4: 0%, Năm 5: 20%, Năm 6: 50%, Năm 7: 100%
    },
}

def calculate_yield(crop_name, temp_min, precipitation):
    """
    Tính toán năng suất dựa trên hằng số năng suất nền và công thức sụt giảm.
    Final_Yield = Baseline_Yield * (1 - Penalty_Sương_Muối) * (1 - Penalty_Mưa_Lớn)
    """
    crop_info = CROP_MAPPING.get(crop_name)
    if not crop_info:
        return 0.0
        
    baseline_yield = crop_info['baseline_yield_ton_per_ha']
    
    penalty_frost = 0.0
    penalty_cold = 0.0
    penalty_rain = 0.0
    
    if temp_min < 5.0:
        penalty_frost = YIELD_PENALTIES['frost_below_5c']
    elif 5.0 <= temp_min <= 10.0:
        penalty_cold = YIELD_PENALTIES['cold_5_to_10c']
        
    if precipitation > 200.0:
        penalty_rain = YIELD_PENALTIES['heavy_rain_200mm']
        
    # Áp dụng sụt giảm
    final_yield = baseline_yield * (1 - penalty_frost) * (1 - penalty_cold) * (1 - penalty_rain)
    return final_yield

def generate_checklist(temp_min, precipitation):
    """
    Sinh mảng checklist hành động theo thời tiết.
    """
    checklist = []
    
    if precipitation > 200:
        checklist.extend(ACTION_CHECKLIST['heavy_rain'])
    if temp_min < 5:
        checklist.extend(ACTION_CHECKLIST['frost'])
    elif 5 <= temp_min <= 10:
        checklist.extend(ACTION_CHECKLIST['cold'])
        
    # Mặc định luôn có normal actions
    if not checklist:
        checklist.extend(ACTION_CHECKLIST['normal'])
        
    return checklist

# ── Hệ số trừng phạt giá theo mức vi phạm sinh thái ──────────
# Khi cây trồng bị trồng sai vùng sinh thái, chất lượng sản phẩm 
# giảm nghiêm trọng → thương lái giáng cấp → giá bán thực tế sụt.
PRICE_PENALTY_FACTORS = {
    # risk_level: (penalty_factor, tên_giáng_cấp, giá_tham_chiếu_mô_tả)
    0: (1.0, None, None),           # AN TOÀN: Giữ nguyên 100% giá
    1: (0.20, "chè xanh thường", "~40.000"),  # THẬN TRỌNG: Bị ép giá còn 20%
    2: (0.0, None, None),           # NGUY HIỂM: Không canh tác → doanh thu = 0
}

def run_decision_engine(crop_name, risk_level, current_price, predicted_price, 
                        capital, area_ha, temp_min, precipitation, mode="Kinh doanh",
                        ecology_violation=None):
    """
    Chạy Decision Engine kết hợp kết quả từ Risk Model và Price Model.
    """
    crop_info = CROP_MAPPING.get(crop_name)
    if not crop_info:
        return None
        
    cost_ratio = crop_info['cost_ratio']
    
    # Tính toán năng suất thực tế
    final_yield_ton_per_ha = calculate_yield(crop_name, temp_min, precipitation)
    total_yield_kg = final_yield_ton_per_ha * area_ha * 1000
    
    # 1. Tính toán tài chính
    # Cấu hình chi phí thực tế duy trì 1 ha (Kinh doanh)
    cost_per_ha_map = {
        "Cà phê Robusta": 80_000_000,   # 80 triệu / ha / năm
        "Cà phê Arabica": 90_000_000,   # 90 triệu / ha / năm
        "Chè Ô Long": 360_000_000,     # 360 triệu / ha / năm (nhân công hái tay chiếm ~50%)
        "Sầu riêng Ri6": 150_000_000    # 150 triệu / ha / năm
    }
    
    base_cost_per_ha = cost_per_ha_map.get(crop_name, 80_000_000)
    
    # ── ÁP DỤNG HỆ SỐ TRỪNG PHẠT GIÁ (Price Penalty) ──
    # Nếu có vi phạm sinh thái → giá bán thực tế bị giáng cấp
    ecology_risk_level = 0
    price_penalty_factor = 1.0
    degraded_product_name = None
    degraded_price_desc = None
    
    if ecology_violation and ecology_violation.get("risk_level", 0) >= 1:
        ecology_risk_level = ecology_violation["risk_level"]
        penalty_info = PRICE_PENALTY_FACTORS.get(ecology_risk_level, (1.0, None, None))
        price_penalty_factor = penalty_info[0]
        degraded_product_name = penalty_info[1]
        degraded_price_desc = penalty_info[2]
    
    # ── LOGIC CHẾ ĐỘ CANH TÁC ──
    long_term_projection = None
    
    if mode == "Kiến thiết":
        # Kiến thiết: Chi phí CAPEX gấp đôi cho năm đầu, doanh thu = 0 (năm 1)
        maturity = CROP_MATURITY_YEARS.get(crop_name, {
            "capex_years": 3, "full_yield_year": 5, "capex_multiplier": 2.0,
            "yield_ramp": [0, 0, 0, 0.30, 0.60, 1.0],
        })
        capex_multiplier = maturity["capex_multiplier"]
        yield_ramp = maturity["yield_ramp"]
        projection_years = len(yield_ramp)
        
        # Chi phí năm đầu = CAPEX (gấp đôi+), các năm sau = duy trì
        base_cost_per_ha_original = base_cost_per_ha
        base_cost_per_ha *= capex_multiplier  # Năm 1 CAPEX
        estimated_revenue = 0.0  # Năm 1 chưa có doanh thu
        
        # ── Tính toán dài hạn từng năm ──
        calc_price = predicted_price if predicted_price else current_price
        actual_selling_price = calc_price * price_penalty_factor
        yearly_breakdown = []
        cumulative_profit = 0
        total_investment = 0
        total_revenue_all = 0
        breakeven_year = 0  # 0 = chưa hoàn vốn trong kỳ
        
        for year_idx in range(projection_years):
            year_num = year_idx + 1
            # Chi phí: Năm 1 CAPEX, các năm sau duy trì
            if year_idx == 0:
                year_cost = base_cost_per_ha * area_ha
            else:
                year_cost = base_cost_per_ha_original * area_ha
            
            # Doanh thu: Theo tỷ lệ năng suất tăng dần
            yield_ratio = yield_ramp[year_idx]
            year_yield_kg = total_yield_kg * yield_ratio
            year_revenue = year_yield_kg * actual_selling_price
            
            year_profit = year_revenue - year_cost
            cumulative_profit += year_profit
            total_investment += year_cost
            total_revenue_all += year_revenue
            
            # Xác định năm hoàn vốn
            if breakeven_year == 0 and cumulative_profit >= 0:
                breakeven_year = year_num
            
            yearly_breakdown.append({
                "year": year_num,
                "cost": year_cost,
                "revenue": year_revenue,
                "profit": year_profit,
                "cumulative_profit": cumulative_profit,
                "yield_ratio_pct": yield_ratio * 100,
            })
        
        # ROI tổng thể = (Tổng doanh thu - Tổng đầu tư) / Tổng đầu tư * 100
        roi_total = ((total_revenue_all - total_investment) / total_investment * 100) if total_investment > 0 else 0
        last_year = yearly_breakdown[-1] if yearly_breakdown else {}
        
        long_term_projection = {
            "projection_years": projection_years,
            "capex_years": maturity["capex_years"],
            "full_yield_year": maturity["full_yield_year"],
            "total_investment": total_investment,
            "total_revenue": total_revenue_all,
            "total_profit": cumulative_profit,
            "roi_total_pct": roi_total,
            "breakeven_year": breakeven_year,
            "estimated_revenue_final_year": last_year.get("revenue", 0),
            "yearly_breakdown": yearly_breakdown,
        }
    else:
        # Kinh doanh: Có doanh thu
        calc_price = predicted_price if predicted_price else current_price
        # ★ ÁP DỤNG TRỪNG PHẠT: Giá thực tế = Giá dự báo × Hệ số trừng phạt
        actual_selling_price = calc_price * price_penalty_factor
        estimated_revenue = total_yield_kg * actual_selling_price
        
    estimated_cost = base_cost_per_ha * area_ha
    
    # Phân chia chi phí (tỷ lệ tham khảo nông nghiệp Lâm Đồng)
    # Chè Ô Long: Nhân công hái tay chiếm ~50% chi phí (6.000-8.000đ/kg búp)
    if crop_name == "Chè Ô Long":
        cost_seeds = estimated_cost * 0.20      # 20% cho giống / vật tư
        cost_fertilizer = estimated_cost * 0.30 # 30% cho phân bón
        cost_labor = estimated_cost * 0.50      # 50% cho nhân công hái tay
    else:
        cost_seeds = estimated_cost * 0.25      # 25% cho giống / vật tư
        cost_fertilizer = estimated_cost * 0.45 # 45% cho phân bón
        cost_labor = estimated_cost * 0.30      # 30% cho nhân công
        
    estimated_profit = estimated_revenue - estimated_cost
    roi_pct = (estimated_profit / estimated_cost) * 100 if estimated_cost > 0 else 0
    breakeven_price = estimated_cost / total_yield_kg if total_yield_kg > 0 else 0
    
    # 2. Sinh thông điệp và kết luận (Quy tắc logic)
    price_trend = "up" if predicted_price > current_price else "down" if predicted_price < current_price else "stable"
    trend_pct = ((predicted_price - current_price) / current_price) * 100 if current_price > 0 else 0
    
    recommendation = ""
    reasoning = ""
    
    if estimated_cost > capital:
        recommendation = "TỪ CHỐI CANH TÁC – Thiếu vốn đầu tư"
        reasoning = f"Chi phí dự kiến ({(estimated_cost/1_000_000_000):.1f} tỷ) vượt quá số vốn cho phép ({(capital/1_000_000_000):.1f} tỷ). Vui lòng giảm diện tích hoặc tăng vốn."
    elif risk_level == 2:
        recommendation = "TỪ CHỐI CANH TÁC – Sai sinh thái hoặc rủi ro cao"
        reasoning = "Khu vực có rủi ro mức độ cao (điều kiện khí hậu hoặc địa hình không phù hợp). Không nên đầu tư."
    elif roi_pct < 0:
        recommendation = "KHÔNG HIỆU QUẢ – Lỗ dự kiến"
        reasoning = f"Dự báo thua lỗ (ROI: {roi_pct:.1f}%). Chi phí canh tác vượt quá doanh thu kỳ vọng từ năng suất."
    elif risk_level == 1 and price_trend == "down":
        recommendation = "THẬN TRỌNG – Giá đang giảm, rủi ro thời tiết trung bình"
        reasoning = f"Dự báo giá giảm {abs(trend_pct):.1f}% và rủi ro thời tiết ở mức chú ý. Nên giảm quy mô đầu tư hoặc chờ thời điểm tốt hơn."
    elif risk_level == 0 and price_trend == "up" and roi_pct > 0:
        recommendation = "THUẬN LỢI – Nên đầu tư"
        reasoning = f"Giá dự báo tăng {abs(trend_pct):.1f}%, rủi ro thời tiết thấp. ROI ước tính {roi_pct:.1f}%."
    else:
        recommendation = "BÌNH THƯỜNG – Canh tác bình thường, theo dõi thêm"
        reasoning = f"Thị trường và thời tiết ổn định, ROI ước tính {roi_pct:.1f}%. Không có biến động bất thường."
        
    # 3. Checklist
    checklist = generate_checklist(temp_min, precipitation)
    
    # ── Sinh cảnh báo tài chính khi bị trừng phạt giá ──
    financial_warning = None
    if ecology_violation and price_penalty_factor < 1.0 and mode != "Kiến thiết":
        original_price = predicted_price if predicted_price else current_price
        penalized_price = original_price * price_penalty_factor
        discount_pct = (1 - price_penalty_factor) * 100
        
        financial_warning = (
            f"⚠️ CẢNH BÁO TÀI CHÍNH: Do sai vùng sinh thái, "
            f"{crop_name} mất hương vị đặc trưng và bị thương lái giáng cấp "
            f"xuống thành {degraded_product_name or 'sản phẩm thường'}. "
            f"Giá bán dự kiến bị ép xuống chỉ còn khoảng "
            f"{degraded_price_desc or f'{penalized_price:,.0f}'.replace(',', '.')} VNĐ/kg "
            f"(Giảm {discount_pct:.0f}% so với giá {crop_name} chuẩn). "
            f"Lợi nhuận sụt giảm nghiêm trọng."
        )
        
        # Cập nhật recommendation nếu bị trừng phạt giá
        if roi_pct < 30:
            # Tìm cây thay thế từ suggestion
            alt_suggestion = ecology_violation.get("suggestion", "")
            recommendation = "THẬN TRỌNG – Lợi nhuận thấp do sai vùng sinh thái"
            reasoning = (
                f"Do trồng sai vùng sinh thái, sản phẩm bị giáng cấp chất lượng, "
                f"giá bán giảm {discount_pct:.0f}%. ROI chỉ còn {roi_pct:.1f}%. "
                f"{alt_suggestion}"
            )
    
    return {
        "financial_analysis": {
            "capital_input": capital,
            "area_ha": area_ha,
            "estimated_cost": estimated_cost,
            "estimated_revenue": estimated_revenue,
            "estimated_profit": estimated_profit,
            "roi_pct": roi_pct,
            "breakeven_price": breakeven_price,
            "cost_breakdown": {
                "seeds": cost_seeds,
                "seeds_label": "🌱 Giống / Cây con" if mode == "Kiến thiết" else "📦 Vật tư & Khấu hao hệ thống",
                "fertilizer": cost_fertilizer,
                "labor": cost_labor
            },
            "price_penalty_applied": price_penalty_factor < 1.0,
            "price_penalty_factor": price_penalty_factor,
            "financial_warning": financial_warning,
            "long_term_projection": long_term_projection,
        },
        "production_decision": {
            "recommendation": recommendation,
            "confidence": 0.85, # hardcoded confidence cho rule-based
            "reasoning": reasoning
        },
        "checklist": checklist,
        "price_trend_info": {
            "trend": price_trend,
            "trend_pct": trend_pct
        }
    }

if __name__ == "__main__":
    # Test thử engine
    res = run_decision_engine(
        crop_name="Sầu riêng Ri6", 
        risk_level=0, 
        current_price=70000, 
        predicted_price=80000, 
        capital=100000000, 
        area_ha=1.0, 
        temp_min=20.0, 
        precipitation=50.0
    )
    print("Kết quả Decision Engine:")
    import json
    print(json.dumps(res, ensure_ascii=False, indent=2))
