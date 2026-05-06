import pandas as pd
import numpy as np
import os
import sys

# Cấu hình UTF-8 cho console Windows để in tiếng Việt không bị lỗi
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


# Thêm thư mục server vào sys.path để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOCATION_MAPPING, RISK_THRESHOLDS

def create_lag_features(df, column_name='price_vnd', lags=[1, 7, 14, 30]):
    """
    Tạo các đặc trưng độ trễ (Time-lags) cho một cột cụ thể.
    Ví dụ: Price_Lag_1, Price_Lag_7, v.v.
    """
    df_out = df.copy()
    # Sắp xếp theo ngày để đảm bảo shift() hoạt động đúng
    df_out = df_out.sort_values(by='date')
    
    for lag in lags:
        df_out[f'{column_name}_Lag_{lag}'] = df_out[column_name].shift(lag)
        
    return df_out

def create_seasonal_features(df, date_col='date'):
    """
    Tạo đặc trưng thời vụ (month, quarter, day_of_week)
    """
    df_out = df.copy()
    df_out[date_col] = pd.to_datetime(df_out[date_col])
    
    df_out['month'] = df_out[date_col].dt.month
    df_out['quarter'] = df_out[date_col].dt.quarter
    df_out['day_of_week'] = df_out[date_col].dt.dayofweek
    
    return df_out

def apply_pseudo_labeling(df, location_name):
    """
    Rule-based Pseudo-Labeling để tạo nhãn Action_Plan (0, 1, 2).
    """
    df_out = df.copy()
    
    elevation = LOCATION_MAPPING.get(location_name, {}).get('elevation', 0)
    
    conditions = []
    choices = []
    
    # --- MỨC 2: NGUY HIỂM (Danger) ---
    # Sầu riêng ở độ cao >= 1400m
    cond_durian_high = (df_out['crop'] == 'Sầu riêng Ri6') & (elevation >= RISK_THRESHOLDS['durian_max_elevation'])
    # Nhiệt độ min < 5 độ
    cond_frost = (df_out['temp_min'] < RISK_THRESHOLDS['frost_temp_celsius'])
    # Mưa > 200mm
    cond_heavy_rain = (df_out['precipitation'] > RISK_THRESHOLDS['heavy_rain_mm_per_week'])
    
    # Gộp điều kiện Mức 2
    cond_level_2 = cond_durian_high | cond_frost | cond_heavy_rain
    
    conditions.append(cond_level_2)
    choices.append(2)
    
    # --- MỨC 1: CHÚ Ý (Warning) ---
    # Lạnh sâu (5-10 độ)
    cond_cold = (df_out['temp_min'] >= RISK_THRESHOLDS['frost_temp_celsius']) & (df_out['temp_min'] < RISK_THRESHOLDS['cold_temp_celsius'])
    # Mưa vừa (100 - 200mm)
    cond_mod_rain = (df_out['precipitation'] > RISK_THRESHOLDS['moderate_rain_mm_per_week']) & (df_out['precipitation'] <= RISK_THRESHOLDS['heavy_rain_mm_per_week'])
    
    # Gộp điều kiện Mức 1
    cond_level_1 = cond_cold | cond_mod_rain
    
    conditions.append(cond_level_1)
    choices.append(1)
    
    # --- MỨC 0: AN TOÀN (Safe) ---
    # Giá trị mặc định là 0
    df_out['risk_label'] = np.select(conditions, choices, default=0)
    
    return df_out

def normalize_features(df, columns):
    """
    Chuẩn hóa Min-Max (Min-Max Scaling) cho các đặc trưng liên tục.
    """
    df_out = df.copy()
    for col in columns:
        if col in df_out.columns:
            min_val = df_out[col].min()
            max_val = df_out[col].max()
            if max_val > min_val:
                df_out[f'{col}_norm'] = (df_out[col] - min_val) / (max_val - min_val)
            else:
                df_out[f'{col}_norm'] = 0.0
    return df_out

def preprocess_data(file_path, location_name):
    """
    Hàm tổng hợp để chạy toàn bộ pipeline Feature Engineering.
    """
    if not os.path.exists(file_path):
        print(f"File không tồn tại: {file_path}")
        return None
        
    print(f"Đang xử lý: {file_path} (Vùng: {location_name})")
    df = pd.read_csv(file_path)
    
    # 1. Tạo seasonal features
    df = create_seasonal_features(df)
    
    # 2. Tạo lag features cho giá
    if 'price_vnd' in df.columns:
        df = create_lag_features(df, column_name='price_vnd', lags=[1, 7, 14, 30])
        # Drop các dòng có NaN do shift
        # Để train XGBoost thì vẫn có thể giữ NaN, nhưng đối với model cơ bản ta có thể drop
        # Hoặc lấp đầy giá trị lag bị khuyết bằng bfill (backfill)
        df.bfill(inplace=True)
    
    # 3. Gắn nhãn pseudo-labeling
    df = apply_pseudo_labeling(df, location_name)
    
    # 4. Chuẩn hóa
    cols_to_norm = ['temp_max', 'temp_min', 'precipitation']
    if 'price_vnd' in df.columns:
        cols_to_norm.append('price_vnd')
    df = normalize_features(df, cols_to_norm)
    
    return df

if __name__ == "__main__":
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    
    # Danh sách các cây trồng và vùng tương ứng
    crops_to_process = [
        ("raw_durian_ri6.csv", "Phường B'Lao", "processed_durian_ri6.csv"),
        ("raw_oolong.csv", "Phường Xuân Trường", "processed_oolong.csv"),
        ("raw_robusta.csv", "Phường B'Lao", "processed_robusta.csv"),
        ("raw_arabica.csv", "Phường Xuân Trường", "processed_arabica.csv"),
    ]
    
    for raw_file, location, out_file in crops_to_process:
        raw_path = os.path.join(data_dir, raw_file)
        df_processed = preprocess_data(raw_path, location)
        
        if df_processed is not None:
            out_path = os.path.join(data_dir, out_file)
            df_processed.to_csv(out_path, index=False)
            print(f"✅ Đã xử lý: {raw_file} -> {out_file} ({len(df_processed)} dòng)")
            print(f"   Phân phối nhãn rủi ro: {df_processed['risk_label'].value_counts().to_dict()}")
            print("-" * 30)
            
    print("🚀 Hoàn tất tiền xử lý dữ liệu!")
