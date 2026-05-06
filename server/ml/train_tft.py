import os
import pandas as pd
import numpy as np
import torch
import joblib
import lightning.pytorch as pl
from lightning.pytorch.callbacks import EarlyStopping, LearningRateMonitor
from lightning.pytorch.loggers import TensorBoardLogger
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.metrics import QuantileLoss
from pytorch_forecasting.data import GroupNormalizer

import warnings
warnings.filterwarnings("ignore")

# Cấu hình đường dẫn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "ai_models")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_tft_model(crop_name):
    print(f"\n--- 🚀 Bắt đầu huấn luyện TFT cho {crop_name} ---")
    
    file_name = f"processed_{crop_name.lower().replace(' ', '_')}.csv"
    file_path = os.path.join(DATA_DIR, file_name)
    
    if not os.path.exists(file_path):
        print(f"❌ Không tìm thấy dữ liệu: {file_path}")
        return
    
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Chuyển đổi các cột categorical sang string (Yêu cầu của pytorch-forecasting)
    cat_cols = ["month", "quarter", "day_of_week"]
    for col in cat_cols:
        df[col] = df[col].astype(str)
    
    # TFT cần time_idx liên tục và group identifier
    df['time_idx'] = range(len(df))
    df['group'] = 0
    
    # Định nghĩa các cột
    max_prediction_length = 30
    max_encoder_length = 90
    training_cutoff = df['time_idx'].max() - max_prediction_length
    
    # Tạo TimeSeriesDataSet
    context_length = max_encoder_length
    prediction_length = max_prediction_length
    
    training = TimeSeriesDataSet(
        df[lambda x: x.time_idx <= training_cutoff],
        time_idx="time_idx",
        target="price_vnd",
        group_ids=["group"],
        min_encoder_length=context_length // 2,
        max_encoder_length=context_length,
        min_prediction_length=1,
        max_prediction_length=prediction_length,
        static_categoricals=[],
        static_reals=[],
        time_varying_known_categoricals=["month", "quarter", "day_of_week"],
        time_varying_known_reals=["temp_max", "temp_min", "precipitation", "time_idx"],
        time_varying_unknown_categoricals=[],
        time_varying_unknown_reals=["price_vnd"],
        target_normalizer=GroupNormalizer(
            groups=["group"], transformation="softplus"
        ),  # dùng softplus cho giá (luôn dương)
        add_relative_time_idx=True,
        add_target_scales=True,
        add_encoder_length=True,
    )
    
    # Tạo validation set
    validation = TimeSeriesDataSet.from_dataset(training, df, predict=True, stop_randomization=True)
    
    # Tạo dataloaders
    batch_size = 64
    train_dataloader = training.to_dataloader(train=True, batch_size=batch_size, num_workers=0)
    val_dataloader = validation.to_dataloader(train=False, batch_size=batch_size * 10, num_workers=0)
    
    # Cấu hình mô hình TFT
    pl.seed_everything(42)
    tft = TemporalFusionTransformer.from_dataset(
        training,
        learning_rate=0.03,
        hidden_size=16,
        attention_head_size=1,
        dropout=0.1,
        hidden_continuous_size=8,
        output_size=7,  # QuantileLoss có 7 quantiles mặc định
        loss=QuantileLoss(),
        log_interval=10,
        reduce_on_plateau_patience=4,
    )
    
    print(f"Số lượng tham số: {tft.size()/1e3:.1f}k")
    
    # Huấn luyện
    trainer = pl.Trainer(
        max_epochs=20, # Để 20 epoch cho nhanh cho đồ án
        accelerator="cpu",
        enable_model_summary=True,
        gradient_clip_val=0.1,
        callbacks=[
            EarlyStopping(monitor="val_loss", patience=5),
            LearningRateMonitor(logging_interval="step")
        ],
    )
    
    trainer.fit(
        tft,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
    )
    
    # Lưu model
    # Lưu cả tft weights và training dataset metadata
    model_path = os.path.join(MODEL_DIR, f"tft_{crop_name.lower().replace(' ', '_')}.pt")
    
    # Chúng ta lưu checkpoint từ trainer hoặc state_dict của model
    # Nhưng cách tốt nhất là lưu cả object model nếu có thể, hoặc dùng torch.save
    torch.save({
        "model_state_dict": tft.state_dict(),
        "model_config": tft.hparams,
        "dataset_parameters": training.get_parameters()
    }, model_path)
    
    print(f"✅ Đã lưu model TFT tại: {model_path}")

if __name__ == "__main__":
    # Huấn luyện cho Robusta và Arabica
    train_tft_model("robusta")
    train_tft_model("arabica")
    print("\n🎉 Hoàn tất huấn luyện toàn bộ mô hình TFT!")
