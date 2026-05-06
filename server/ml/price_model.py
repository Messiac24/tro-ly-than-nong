import pandas as pd
import numpy as np
import os
import sys
import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

# Cấu hình UTF-8 cho console Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Thêm thư mục server vào sys.path để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CROP_MAPPING

# ── XGBOOST REGRESSOR ─────────────────────────────────────────

def train_xgboost(df, crop_name, model_dir):
    """
    Huấn luyện mô hình XGBoost Regressor cho một loại cây cụ thể.
    """
    print(f"\n--- Bắt đầu huấn luyện XGBoost cho {crop_name} ---")
    
    features = [
        'month', 'quarter', 'day_of_week',
        'temp_max', 'temp_min', 'precipitation',
        'price_vnd_Lag_1', 'price_vnd_Lag_7', 'price_vnd_Lag_14', 'price_vnd_Lag_30'
    ]
    target = 'price_vnd'
    
    df_clean = df.dropna(subset=features + [target]).copy()
    
    if len(df_clean) < 100:
        print(f"Cảnh báo: Dữ liệu quá ít cho XGBoost.")
        return None
        
    X = df_clean[features]
    y = df_clean[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        objective='reg:squarederror'
    )
    
    model.fit(X_train, y_train, verbose=False)
    
    # Lưu mô hình
    model_filename = f"xgb_{crop_name.lower().replace(' ', '_').replace('ê', 'e').replace('ô', 'o')}.pkl"
    model_path = os.path.join(model_dir, model_filename)
    joblib.dump(model, model_path)
    print(f"Đã lưu mô hình XGBoost tại: {model_path}")
    
    return model

# ── TEMPORAL FUSION TRANSFORMER (TFT) ─────────────────────────
# Yêu cầu: pytorch, pytorch-forecasting, lightning

def train_tft(df, crop_name, model_dir):
    """
    Huấn luyện mô hình TFT (Temporal Fusion Transformer).
    Đây là mô hình Deep Learning tiên tiến cho Time-Series.
    """
    print(f"\n--- Bắt đầu cấu hình & huấn luyện TFT cho {crop_name} ---")
    
    try:
        from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
        from pytorch_forecasting.metrics import QuantileLoss
        import lightning.pytorch as pl
        from lightning.pytorch.callbacks import EarlyStopping
        
        # 1. Chuẩn bị dữ liệu cho TFT
        # TFT cần cột 'time_idx' (thời gian liên tục), 'group' (định danh chuỗi)
        df = df.copy()
        df['time_idx'] = range(len(df))
        df['group'] = 0 # Giả định một nhóm duy nhất
        
        # 2. Định nghĩa TimeSeriesDataSet
        max_prediction_length = 30
        max_encoder_length = 90
        
        training_cutoff = df['time_idx'].max() - max_prediction_length
        
        training = TimeSeriesDataSet(
            df[lambda x: x.time_idx <= training_cutoff],
            time_idx="time_idx",
            target="price_vnd",
            group_ids=["group"],
            min_encoder_length=max_encoder_length // 2,
            max_encoder_length=max_encoder_length,
            min_prediction_length=1,
            max_prediction_length=max_prediction_length,
            static_categoricals=[],
            static_reals=[],
            time_varying_known_categoricals=["month", "quarter", "day_of_week"],
            time_varying_known_reals=["temp_max", "temp_min", "precipitation"],
            time_varying_unknown_categoricals=[],
            time_varying_unknown_reals=["price_vnd"],
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,
        )
        
        # 3. Tạo DataLoader
        validation = TimeSeriesDataSet.from_dataset(training, df, predict=True, stop_randomization=True)
        train_dataloader = training.to_dataloader(train=True, batch_size=32, num_workers=0)
        val_dataloader = validation.to_dataloader(train=False, batch_size=32, num_workers=0)
        
        # 4. Khởi tạo mô hình TFT
        tft = TemporalFusionTransformer.from_dataset(
            training,
            learning_rate=0.03,
            hidden_size=16,
            attention_head_size=1,
            dropout=0.1,
            hidden_continuous_size=8,
            output_size=7,  # 7 quantiles theo mặc định
            loss=QuantileLoss(),
            log_interval=10,
            reduce_on_plateau_patience=4,
        )
        
        # 5. Huấn luyện với PyTorch Lightning
        trainer = pl.Trainer(
            max_epochs=30,
            accelerator="cpu", # Dùng CPU cho đồ án nhẹ
            enable_model_summary=True,
            gradient_clip_val=0.1,
            callbacks=[EarlyStopping(monitor="val_loss", patience=5)],
        )
        
        print("Đang huấn luyện TFT (Deep Learning)...")
        # trainer.fit(tft, train_dataloaders=train_dataloader, val_dataloaders=val_dataloader)
        print("Huấn luyện hoàn tất (Simulated for Demo).")
        
        # Lưu mô hình
        model_path = os.path.join(model_dir, f"tft_{crop_name.lower().replace(' ', '_')}.pkl")
        joblib.dump(tft, model_path)
        print(f"Đã lưu mô hình TFT tại: {model_path}")
        
    except ImportError:
        print("Lỗi: Thiếu thư viện pytorch-forecasting. Vui lòng cài đặt để chạy TFT.")
    except Exception as e:
        print(f"Lỗi khi huấn luyện TFT: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    model_dir = os.path.join(base_dir, "ai_models")
    
    # Huấn luyện XGBoost cho Sầu riêng & Chè
    for crop in ["Sầu riêng Ri6", "Chè Ô Long"]:
        file_name = f"processed_{crop.lower().replace(' ', '_').replace('ê', 'e').replace('ô', 'o')}.csv"
        file_path = os.path.join(data_dir, file_name)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            train_xgboost(df, crop, model_dir)
            
    # Huấn luyện TFT cho Cà phê (Demo cấu hình)
    dummy_df = pd.DataFrame({
        'price_vnd': np.random.normal(120000, 5000, 200),
        'temp_max': np.random.normal(28, 2, 200),
        'temp_min': np.random.normal(18, 2, 200),
        'precipitation': np.random.normal(10, 5, 200),
        'month': [1]*200, 'quarter': [1]*200, 'day_of_week': [1]*200
    })
    train_tft(dummy_df, "Cà phê Robusta", model_dir)
