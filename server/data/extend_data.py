"""
Script mở rộng dữ liệu CSV từ 2020-01-01 đến 2024-04-26
và ghép vào trước dữ liệu hiện có (2024-04-27 → 2026-04-27).

Kết quả: Mỗi file CSV sẽ có phạm vi 2020-01-01 → 2026-04-27.

Dữ liệu giá mô phỏng thực tế:
  - Có xu hướng dài hạn (trend) tăng dần qua các năm
  - Có tính mùa vụ (seasonality) theo tháng
  - Có nhiễu ngẫu nhiên (noise) ngày-qua-ngày
  - Giá cuối cùng (2024-04-26) phải khớp mượt với giá đầu tiên hiện có (2024-04-27)

Thời tiết mô phỏng theo vùng:
  - B'Lao (800m): Nóng hơn, mưa nhiều mùa mưa (T5-T10)
  - Xuân Trường / Đà Lạt (1500m): Mát hơn, sương giá mùa đông
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

np.random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════
# CẤU HÌNH TỪNG CÂY TRỒNG
# ═══════════════════════════════════════════════════════════

CROP_CONFIG = {
    "arabica": {
        "crop_name": "Cà phê Arabica",
        "location": "dalat",  # Xuân Trường - Đà Lạt (1500m)
        # Giá Arabica: từ ~100k (2020) tăng dần lên ~152k (04/2024)
        "price_base_2020": 98000,
        "price_target_202404": 152200,  # Giá đầu tiên trong file hiện tại
        "price_noise_std": 1800,
        # Tính mùa vụ: Thu hoạch T11-T1 (giá giảm), khan hiếm T6-T9 (giá tăng)
        "seasonal_amplitude": 3500,
        "seasonal_peak_month": 8,  # Đỉnh giá tháng 8
        "raw_file": "raw_arabica.csv",
        "processed_file": "processed_arabica.csv",
    },
    "robusta": {
        "crop_name": "Cà phê Robusta",
        "location": "blao",  # B'Lao (800m)
        # Giá Robusta: từ ~75k (2020) tăng lên ~118k (04/2024) - tăng mạnh 2022-2024
        "price_base_2020": 72000,
        "price_target_202404": 118700,
        "price_noise_std": 2000,
        "seasonal_amplitude": 3000,
        "seasonal_peak_month": 7,
        "raw_file": "raw_robusta.csv",
        "processed_file": "processed_robusta.csv",
    },
    "durian_ri6": {
        "crop_name": "Sầu riêng Ri6",
        "location": "blao",
        # Giá sầu riêng: biến động mạnh theo mùa, từ ~45k (2020) lên ~85k (04/2024)
        "price_base_2020": 42000,
        "price_target_202404": 85000,
        "price_noise_std": 5000,
        # Mùa thu hoạch T6-T8: giá GIẢM (dư cung), T1-T4: giá TĂNG (khan hiếm)
        "seasonal_amplitude": 12000,
        "seasonal_peak_month": 2,  # Đỉnh giá tháng 2 (trái vụ)
        "raw_file": "raw_durian_ri6.csv",
        "processed_file": "processed_durian_ri6.csv",
    },
    "oolong": {
        "crop_name": "Chè Ô Long",
        "location": "dalat",
        # Giá Ô Long: ổn định hơn, từ ~200k (2020) lên ~260k (04/2024)
        "price_base_2020": 195000,
        "price_target_202404": 260000,
        "price_noise_std": 4000,
        # Thu hoạch rải rác quanh năm, biến động mùa vụ nhẹ
        "seasonal_amplitude": 5000,
        "seasonal_peak_month": 3,  # Đỉnh giá đầu năm (chè xuân cao cấp)
        "raw_file": "raw_oolong.csv",
        "processed_file": "processed_oolong.csv",
    },
}

# ═══════════════════════════════════════════════════════════
# MÔ PHỎNG THỜI TIẾT THEO VÙNG & THÁNG
# ═══════════════════════════════════════════════════════════

# B'Lao (800m) - Nhiệt đới gió mùa
WEATHER_BLAO = {
    # month: (temp_max_mean, temp_max_std, temp_min_mean, temp_min_std, precip_mean, precip_std)
    1:  (32.0, 1.5, 18.0, 1.5,  2.0,  4.0),
    2:  (33.0, 1.5, 18.5, 1.5,  1.5,  3.0),
    3:  (34.0, 1.5, 20.0, 1.5,  5.0,  8.0),
    4:  (34.0, 1.5, 21.0, 1.5, 10.0, 12.0),
    5:  (32.0, 1.5, 21.5, 1.0, 18.0, 15.0),
    6:  (30.0, 1.5, 21.0, 1.0, 22.0, 18.0),
    7:  (29.5, 1.5, 20.5, 1.0, 25.0, 20.0),
    8:  (29.5, 1.5, 20.5, 1.0, 25.0, 20.0),
    9:  (30.0, 1.5, 20.5, 1.0, 22.0, 18.0),
    10: (30.5, 1.5, 20.0, 1.5, 15.0, 14.0),
    11: (31.0, 1.5, 19.5, 1.5,  8.0, 10.0),
    12: (31.0, 1.5, 18.5, 1.5,  3.0,  5.0),
}

# Đà Lạt / Xuân Trường (1500m) - Ôn đới núi cao
WEATHER_DALAT = {
    1:  (24.0, 1.5, 11.0, 2.0,  1.5,  3.0),
    2:  (25.0, 1.5, 11.5, 2.0,  1.0,  2.5),
    3:  (26.0, 1.5, 13.0, 1.5,  3.0,  5.0),
    4:  (26.0, 1.5, 15.0, 1.5,  7.0, 10.0),
    5:  (25.0, 1.5, 16.5, 1.0, 14.0, 12.0),
    6:  (24.0, 1.2, 16.5, 1.0, 16.0, 14.0),
    7:  (23.5, 1.2, 16.0, 1.0, 18.0, 15.0),
    8:  (23.5, 1.2, 16.0, 1.0, 18.0, 15.0),
    9:  (24.0, 1.2, 16.0, 1.0, 16.0, 14.0),
    10: (24.0, 1.5, 15.5, 1.5, 12.0, 12.0),
    11: (23.5, 1.5, 13.5, 2.0,  5.0,  8.0),
    12: (23.0, 1.5, 11.5, 2.5,  2.0,  4.0),
}


def generate_weather(location: str, dates: list) -> pd.DataFrame:
    """Sinh dữ liệu thời tiết theo vùng cho danh sách ngày."""
    weather_table = WEATHER_DALAT if location == "dalat" else WEATHER_BLAO
    
    records = []
    for d in dates:
        m = d.month
        tm_mean, tm_std, tn_mean, tn_std, pr_mean, pr_std = weather_table[m]
        
        temp_max = round(np.random.normal(tm_mean, tm_std), 1)
        temp_min = round(np.random.normal(tn_mean, tn_std), 1)
        precipitation = round(max(0, np.random.exponential(pr_mean)), 1)
        
        # Đảm bảo logic
        temp_max = max(temp_max, 16.0)
        temp_min = min(temp_min, temp_max - 3.0)
        temp_min = max(temp_min, 5.0)
        
        records.append({
            "date": d.strftime("%Y-%m-%d"),
            "temp_max": temp_max,
            "temp_min": temp_min,
            "precipitation": precipitation,
        })
    
    return pd.DataFrame(records)


def generate_prices(config: dict, n_days: int, target_last_price: float) -> np.ndarray:
    """
    Sinh chuỗi giá mô phỏng thực tế:
      - Xu hướng tăng dần từ price_base_2020 đến target_last_price
      - Tính mùa vụ
      - Nhiễu ngẫu nhiên (random walk)
      - Giá cuối khớp target
    """
    base = config["price_base_2020"]
    noise_std = config["price_noise_std"]
    seasonal_amp = config["seasonal_amplitude"]
    peak_month = config["seasonal_peak_month"]
    
    # 1. Xu hướng tuyến tính
    trend = np.linspace(base, target_last_price, n_days)
    
    # 2. Tính mùa vụ (sin wave, đỉnh ở peak_month)
    start_date = datetime(2020, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    seasonal = np.array([
        seasonal_amp * np.sin(2 * np.pi * ((d.month - peak_month) / 12.0))
        for d in dates
    ])
    
    # 3. Nhiễu (random walk có mean-reversion)
    noise = np.zeros(n_days)
    for i in range(1, n_days):
        # Mean-reverting random walk
        noise[i] = noise[i-1] * 0.92 + np.random.normal(0, noise_std * 0.3)
    
    # 4. Kết hợp
    prices = trend + seasonal + noise
    
    # 5. Điều chỉnh để giá cuối cùng khớp target
    # Dùng linear correction dần dần ở 30 ngày cuối
    correction = target_last_price - prices[-1]
    correction_ramp = np.zeros(n_days)
    ramp_days = min(60, n_days)
    correction_ramp[-ramp_days:] = np.linspace(0, correction, ramp_days)
    prices += correction_ramp
    
    # 6. Làm tròn theo đơn vị hợp lý
    if config["crop_name"] == "Sầu riêng Ri6":
        prices = np.round(prices / 1000) * 1000  # Làm tròn 1000đ
    elif config["crop_name"] == "Chè Ô Long":
        prices = np.round(prices / 1000) * 1000  # Làm tròn 1000đ
    else:
        prices = np.round(prices / 100) * 100    # Làm tròn 100đ
    
    # Đảm bảo giá dương
    prices = np.maximum(prices, base * 0.5)
    
    return prices, dates


def build_raw_df(config: dict) -> pd.DataFrame:
    """Tạo raw DataFrame cho giai đoạn 2020-01-01 → 2024-04-26."""
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 4, 26)
    n_days = (end_date - start_date).days + 1  # Bao gồm cả 2 đầu
    
    prices, dates = generate_prices(config, n_days, config["price_target_202404"])
    weather_df = generate_weather(config["location"], dates)
    
    df = weather_df.copy()
    df["crop"] = config["crop_name"]
    df["price_vnd"] = prices
    df["source"] = "AI_Synthetic"
    df["is_synthetic"] = True
    
    return df


def build_processed_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Thêm các cột feature engineering vào raw data."""
    df = raw_df.copy()
    
    # Cột thời gian
    df["date_dt"] = pd.to_datetime(df["date"])
    df["month"] = df["date_dt"].dt.month
    df["quarter"] = df["date_dt"].dt.quarter
    df["day_of_week"] = df["date_dt"].dt.dayofweek
    
    # Lag features
    df["price_vnd_Lag_1"] = df["price_vnd"].shift(1).fillna(df["price_vnd"].iloc[0])
    df["price_vnd_Lag_7"] = df["price_vnd"].shift(7).fillna(df["price_vnd"].iloc[0])
    df["price_vnd_Lag_14"] = df["price_vnd"].shift(14).fillna(df["price_vnd"].iloc[0])
    df["price_vnd_Lag_30"] = df["price_vnd"].shift(30).fillna(df["price_vnd"].iloc[0])
    
    # Risk label (0 = safe, 1 = warning) - phần lớn safe, một số ít warning
    df["risk_label"] = 0
    # Thêm một số ngày rủi ro khi thời tiết xấu
    heavy_rain = df["precipitation"] > 50
    cold = df["temp_min"] < 8
    df.loc[heavy_rain | cold, "risk_label"] = 1
    
    df.drop(columns=["date_dt"], inplace=True)
    
    return df


def normalize_processed(df_full: pd.DataFrame) -> pd.DataFrame:
    """Tính lại normalized columns cho toàn bộ dataset sau khi ghép."""
    df = df_full.copy()
    
    # Normalize temp_max: (x - min) / (max - min) 
    tmax_min = df["temp_max"].min()
    tmax_max = df["temp_max"].max()
    df["temp_max_norm"] = (df["temp_max"] - tmax_min) / (tmax_max - tmax_min) if tmax_max > tmax_min else 0
    
    # Normalize temp_min
    tmin_min = df["temp_min"].min()
    tmin_max = df["temp_min"].max()
    df["temp_min_norm"] = (df["temp_min"] - tmin_min) / (tmin_max - tmin_min) if tmin_max > tmin_min else 0
    
    # Normalize precipitation
    pr_min = df["precipitation"].min()
    pr_max = df["precipitation"].max()
    df["precipitation_norm"] = (df["precipitation"] - pr_min) / (pr_max - pr_min) if pr_max > pr_min else 0
    
    # Normalize price
    p_min = df["price_vnd"].min()
    p_max = df["price_vnd"].max()
    df["price_vnd_norm"] = (df["price_vnd"] - p_min) / (p_max - p_min) if p_max > p_min else 0
    
    return df


def recalculate_lags_at_junction(df: pd.DataFrame) -> pd.DataFrame:
    """Tính lại lag features tại điểm nối giữa dữ liệu cũ và mới."""
    df = df.copy()
    df["price_vnd_Lag_1"] = df["price_vnd"].shift(1).fillna(df["price_vnd"].iloc[0])
    df["price_vnd_Lag_7"] = df["price_vnd"].shift(7).fillna(df["price_vnd"].iloc[0])
    df["price_vnd_Lag_14"] = df["price_vnd"].shift(14).fillna(df["price_vnd"].iloc[0])
    df["price_vnd_Lag_30"] = df["price_vnd"].shift(30).fillna(df["price_vnd"].iloc[0])
    return df


def process_crop(key: str, config: dict):
    """Xử lý 1 cây trồng: tạo data mới + ghép + lưu."""
    print(f"\n{'='*60}")
    print(f"  Đang xử lý: {config['crop_name']}")
    print(f"{'='*60}")
    
    # 1. Đọc dữ liệu hiện có
    raw_existing = pd.read_csv(os.path.join(DATA_DIR, config["raw_file"]))
    proc_existing = pd.read_csv(os.path.join(DATA_DIR, config["processed_file"]))
    
    print(f"  Dữ liệu hiện có: {raw_existing['date'].iloc[0]} → {raw_existing['date'].iloc[-1]} ({len(raw_existing)} dòng)")
    
    # 2. Tạo dữ liệu mới (2020-01-01 → 2024-04-26)
    new_raw = build_raw_df(config)
    print(f"  Dữ liệu mới tạo: {new_raw['date'].iloc[0]} → {new_raw['date'].iloc[-1]} ({len(new_raw)} dòng)")
    print(f"  Giá đầu (2020-01-01): {new_raw['price_vnd'].iloc[0]:,.0f}")
    print(f"  Giá cuối (2024-04-26): {new_raw['price_vnd'].iloc[-1]:,.0f}")
    print(f"  Giá đầu file cũ (2024-04-27): {raw_existing['price_vnd'].iloc[0]:,.0f}")
    
    # 3. Ghép RAW
    raw_combined = pd.concat([new_raw, raw_existing], ignore_index=True)
    raw_combined.to_csv(os.path.join(DATA_DIR, config["raw_file"]), index=False, encoding="utf-8-sig")
    print(f"  ✅ RAW lưu xong: {raw_combined['date'].iloc[0]} → {raw_combined['date'].iloc[-1]} ({len(raw_combined)} dòng)")
    
    # 4. Xử lý PROCESSED
    new_processed = build_processed_df(new_raw)
    
    # Ghép: dữ liệu mới + dữ liệu cũ
    # Loại bỏ cột norm cũ (sẽ tính lại)
    norm_cols = ["temp_max_norm", "temp_min_norm", "precipitation_norm", "price_vnd_norm"]
    proc_existing_clean = proc_existing.drop(columns=[c for c in norm_cols if c in proc_existing.columns], errors='ignore')
    new_processed_clean = new_processed.drop(columns=[c for c in norm_cols if c in new_processed.columns], errors='ignore')
    
    proc_combined = pd.concat([new_processed_clean, proc_existing_clean], ignore_index=True)
    
    # Tính lại lags cho toàn bộ (để nối mượt)
    proc_combined = recalculate_lags_at_junction(proc_combined)
    
    # Tính lại normalization cho toàn bộ
    proc_combined = normalize_processed(proc_combined)
    
    # Đảm bảo thứ tự cột đúng
    expected_cols = [
        "date", "temp_max", "temp_min", "precipitation", "crop", "price_vnd",
        "source", "is_synthetic", "month", "quarter", "day_of_week",
        "price_vnd_Lag_1", "price_vnd_Lag_7", "price_vnd_Lag_14", "price_vnd_Lag_30",
        "risk_label", "temp_max_norm", "temp_min_norm", "precipitation_norm", "price_vnd_norm"
    ]
    proc_combined = proc_combined[expected_cols]
    
    proc_combined.to_csv(os.path.join(DATA_DIR, config["processed_file"]), index=False, encoding="utf-8-sig")
    print(f"  ✅ PROCESSED lưu xong: {proc_combined['date'].iloc[0]} → {proc_combined['date'].iloc[-1]} ({len(proc_combined)} dòng)")


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  MỞ RỘNG DỮ LIỆU CSV: 2020-01-01 → 2026-04-27      ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    # Backup
    print("\n📦 Tạo backup...")
    for key, config in CROP_CONFIG.items():
        for fname in [config["raw_file"], config["processed_file"]]:
            src = os.path.join(DATA_DIR, fname)
            dst = os.path.join(DATA_DIR, fname + ".bak")
            if os.path.exists(src):
                import shutil
                shutil.copy2(src, dst)
                print(f"  Backup: {fname} → {fname}.bak")
    
    # Xử lý từng cây trồng
    for key, config in CROP_CONFIG.items():
        process_crop(key, config)
    
    # Kiểm tra kết quả
    print(f"\n{'='*60}")
    print("📊 KIỂM TRA KẾT QUẢ:")
    print(f"{'='*60}")
    for key, config in CROP_CONFIG.items():
        df = pd.read_csv(os.path.join(DATA_DIR, config["raw_file"]))
        print(f"  {config['crop_name']:20s}: {df['date'].iloc[0]} → {df['date'].iloc[-1]} ({len(df):,} dòng)")
    
    print("\n✅ Hoàn tất!")


if __name__ == "__main__":
    main()
