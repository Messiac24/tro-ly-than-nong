import os
import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import warnings

# Ẩn các cảnh báo lệch phiên bản thư viện để làm sạch Log
warnings.filterwarnings("ignore", category=UserWarning)
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except ImportError:
    pass

# Thêm thư mục server vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOCATION_MAPPING, CROP_MAPPING, RISK_THRESHOLDS

# Ánh xạ tên cây trồng sang file cơ sở
CROP_FILE_MAP = {
    "Cà phê Robusta": "robusta",
    "Cà phê Arabica": "arabica",
    "Sầu riêng Ri6": "durian_ri6",
    "Chè Ô Long": "oolong"
}

import torch
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer

# --- FIX: Bản vá cho lỗi StringDtype khi unpickle mô hình ---
import pandas as pd
try:
    from pandas.api.types import StringDtype
    def _fix_string_dtype_unpickle():
        import pandas._libs.arrays as pandas_arrays
        # Đảm bảo StringDtype có thể nhận thêm đối số nếu cần (tùy phiên bản)
        original_init = StringDtype.__init__
        def patched_init(self, *args, **kwargs):
            if len(args) > 1: # Nếu có dư đối số (lỗi 3 đối số)
                args = args[:1]
            return original_init(self, *args, **kwargs)
        StringDtype.__init__ = patched_init
    _fix_string_dtype_unpickle()
except Exception:
    pass
# -----------------------------------------------------------

# Đường dẫn tới thư mục chứa models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ai_models")
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_pkl(filename):
    path = os.path.join(MODEL_DIR, filename)
    if os.path.exists(path):
        return joblib.load(path)
    return None

def load_tft_model(crop_name_key):
    """Load model TFT và tham số dataset từ file .pt"""
    file_base = CROP_FILE_MAP.get(crop_name_key, crop_name_key.lower().replace(' ', '_'))
    path = os.path.join(MODEL_DIR, f"tft_{file_base}.pt")
    if not os.path.exists(path):
        return None
    
    try:
        # Load checkpoint an toàn
        checkpoint = torch.load(path, map_location=torch.device('cpu'), weights_only=False)
        params = checkpoint["dataset_parameters"]
        
        # Lấy giá trị thực tế từ file để tránh lỗi lọc dữ liệu do độ dài encoder
        file_name = f"processed_{file_base}.csv"
        csv_path = os.path.join(DATA_DIR, file_name)
        if not os.path.exists(csv_path):
            return None
            
        df_sample = pd.read_csv(csv_path)
        df_sample = df_sample.tail(100).copy() # Lấy 100 dòng cuối là đủ cho encoder (90)
        df_sample['time_idx'] = range(len(df_sample))
        df_sample['group'] = 0
        
        for col in params.get("time_varying_known_categoricals", []):
            df_sample[col] = df_sample[col].astype(str)
        
        # Khôi phục TimeSeriesDataSet parameters
        dataset = TimeSeriesDataSet.from_parameters(params, df_sample)
        
        tft = TemporalFusionTransformer.from_dataset(
            dataset,
            **checkpoint["model_config"]
        )
        tft.load_state_dict(checkpoint["model_state_dict"])
        tft.eval()
        
        return {
            "model": tft,
            "params": params
        }
    except Exception as e:
        print(f"❌ Cảnh báo: Không thể tải mô hình {crop_name_key} do lỗi: {e}")
        return None

# Load models globally to avoid reloading on every request
RISK_MODEL = load_pkl("risk_rf.pkl")
DURIAN_MODEL = load_pkl("xgb_sau_rieng_ri6.pkl")
OOLONG_MODEL = load_pkl("xgb_che_o_long.pkl")

# Cache cho TFT models
TFT_MODELS = {
    "Cà phê Robusta": load_tft_model("Cà phê Robusta"),
    "Cà phê Arabica": load_tft_model("Cà phê Arabica")
}

import requests
from functools import lru_cache

@lru_cache(maxsize=32)
def get_weather(location_name="Phường B'Lao"):
    """
    Lấy dữ liệu thời tiết thực tế từ Open-Meteo.
    """
    loc_info = LOCATION_MAPPING.get(location_name, LOCATION_MAPPING["Phường B'Lao"])
    lat = loc_info["coordinates"]["lat"]
    lon = loc_info["coordinates"]["lon"]
    
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Asia/Ho_Chi_Minh&forecast_days=1"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        return {
            "temp_max": data["daily"]["temperature_2m_max"][0],
            "temp_min": data["daily"]["temperature_2m_min"][0],
            "precipitation": data["daily"]["precipitation_sum"][0]
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        # Fallback to mock data if API fails
        return {
            "temp_max": 28.5,
            "temp_min": 19.0,
            "precipitation": 15.0
        }

def predict_risk(location_name, crop_name):
    """
    Dự báo mức độ rủi ro bằng Random Forest
    """
    if not RISK_MODEL:
        return 0, 0.1 # Default safe
    
    loc_info = LOCATION_MAPPING.get(location_name, {})
    elevation = loc_info.get("elevation", 1000)
    weather = get_weather(location_name)
    
    # Chuẩn bị input cho RF: ['temp_max', 'temp_min', 'precipitation', 'elevation']
    X = pd.DataFrame([[
        weather['temp_max'], 
        weather['temp_min'], 
        weather['precipitation'], 
        elevation
    ]], columns=['temp_max', 'temp_min', 'precipitation', 'elevation'])
    
    risk_level = int(RISK_MODEL.predict(X)[0])
    risk_proba = RISK_MODEL.predict_proba(X).max()
    
    return risk_level, risk_proba

def predict_price(crop_name, current_price, location_name="Phường B'Lao"):
    """
    Dự báo giá bằng XGBoost hoặc TFT
    """
    crop_info = CROP_MAPPING.get(crop_name, {})
    model_type = crop_info.get("model_type")
    
    # ── Chọn model tương ứng ──
    model = None
    if crop_name == "Sầu riêng Ri6":
        model = DURIAN_MODEL
    elif crop_name == "Chè Ô Long":
        model = OOLONG_MODEL
    elif crop_name in ["Cà phê Robusta", "Cà phê Arabica"]:
        # Placeholder cho TFT model (sẽ load từ pkl/pth sau khi train)
        # model = load_pkl(f"tft_{crop_name.lower().replace(' ', '_')}.pkl")
        pass
        
    forecast = []
    base_date = datetime.now()
    
    if model and model_type == "xgboost":
        # Dự báo đệ quy (Recursive multi-step forecast) cho 30 ngày
        temp_price = current_price
        weather = get_weather(location_name)
        
        # Lấy các đặc trưng thời gian
        current_date = base_date
        
        for i in range(1, 31):
            current_date += timedelta(days=1)
            month = current_date.month
            quarter = (month - 1) // 3 + 1
            day_of_week = current_date.weekday()
            
            # Features: ['month', 'quarter', 'day_of_week', 'temp_max', 'temp_min', 'precipitation', 'price_vnd_Lag_1', '7', '14', '30']
            # Dùng temp_price làm Lag_1, và giả lập các lag khác từ temp_price
            X = pd.DataFrame([[
                month, quarter, day_of_week,
                weather['temp_max'], weather['temp_min'], weather['precipitation'],
                temp_price, temp_price * 0.99, temp_price * 1.01, temp_price * 0.98
            ]], columns=['month', 'quarter', 'day_of_week', 'temp_max', 'temp_min', 'precipitation', 
                         'price_vnd_Lag_1', 'price_vnd_Lag_7', 'price_vnd_Lag_14', 'price_vnd_Lag_30'])
            
            pred_val = float(model.predict(X)[0])
            
            # Giới hạn biến động thực tế (không quá 2% mỗi ngày)
            max_change = temp_price * 0.02
            pred_val = max(temp_price - max_change, min(temp_price + max_change, pred_val))
            
            forecast.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "min": pred_val * 0.97,
                "predicted": pred_val,
                "max": pred_val * 1.03
            })
            temp_price = pred_val # Cập nhật cho ngày kế tiếp
            
    elif model_type == "tft":
        # ── LOGIC TFT THỰC TẾ ──
        tft_data = TFT_MODELS.get(crop_name)
        if not tft_data:
            # Fallback nếu chưa có model
            trend_factor = 1.001
            for i in range(1, 31):
                target_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
                predicted = current_price * (trend_factor ** i) + (np.random.normal(0, 300))
                forecast.append({"date": target_date, "min": predicted * 0.96, "predicted": predicted, "max": predicted * 1.04})
            return forecast

        model = tft_data["model"]
        params = tft_data["params"]
        
        # 1. Load dữ liệu lịch sử để làm ngữ cảnh (Encoder)
        file_base = CROP_FILE_MAP.get(crop_name, crop_name.lower().replace(' ', '_'))
        file_name = f"processed_{file_base}.csv"
        df_hist = pd.read_csv(os.path.join(DATA_DIR, file_name))
        df_hist = df_hist.tail(90).copy() # Lấy 90 ngày cuối
        df_hist['time_idx'] = range(len(df_hist))
        df_hist['group'] = 0
        
        # 2. Tạo dữ liệu dự báo cho 30 ngày tới (Decoder)
        last_idx = df_hist['time_idx'].max()
        future_dates = [base_date + timedelta(days=i) for i in range(1, 31)]
        df_future = pd.DataFrame({
            "date": future_dates,
            "time_idx": range(last_idx + 1, last_idx + 31),
            "group": 0,
            "price_vnd": current_price # Seed value
        })
        
        # Thêm các feature thời gian cho future
        df_future['month'] = df_future['date'].dt.month.astype(str)
        df_future['quarter'] = df_future['date'].dt.quarter.astype(str)
        df_future['day_of_week'] = df_future['date'].dt.dayofweek.astype(str)
        
        # Giả lập thời tiết tương lai (lấy weather hiện tại làm base)
        weather = get_weather(location_name)
        df_future['temp_max'] = weather['temp_max']
        df_future['temp_min'] = weather['temp_min']
        df_future['precipitation'] = weather['precipitation']
        
        # Chuyển đổi categorical cho hist
        for col in ["month", "quarter", "day_of_week"]:
            df_hist[col] = df_hist[col].astype(str)
            
        # Kết hợp hist + future
        df_combined = pd.concat([df_hist, df_future], ignore_index=True)
        
        # 3. Chạy Inference
        new_raw_data = TimeSeriesDataSet.from_parameters(params, df_combined, predict=True)
        
        with torch.no_grad():
            # Trả về quantiles (7 quantiles)
            # 0.02, 0.1, 0.25, 0.5, 0.75, 0.9, 0.98
            # Chúng ta lấy index 3 (0.5) làm dự báo chính, index 1 (0.1) làm min, index 5 (0.9) làm max
            prediction = model.predict(new_raw_data, mode="quantiles")[0]
            
            for i in range(30):
                pred_val = float(prediction[i, 3]) # Median
                min_val = float(prediction[i, 1])
                max_val = float(prediction[i, 5])
                
                target_date = future_dates[i].strftime("%Y-%m-%d")
                forecast.append({
                    "date": target_date,
                    "min": min_val,
                    "predicted": pred_val,
                    "max": max_val
                })
    else:
        # Fallback
        for i in range(1, 31):
            target_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            predicted = current_price * (1 + (np.random.normal(0, 0.005) * i))
            forecast.append({
                "date": target_date,
                "min": predicted * 0.95,
                "predicted": predicted,
                "max": predicted * 1.05
            })
            
    return forecast
