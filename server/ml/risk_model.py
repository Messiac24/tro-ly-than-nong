import pandas as pd
import numpy as np
import os
import sys

# Cấu hình UTF-8 cho console Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib

# Thêm thư mục server vào sys.path để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOCATION_MAPPING

def train_risk_model(model_dir, data_dir):
    """
    Huấn luyện mô hình Random Forest Classifier để đánh giá rủi ro
    dựa trên pseudo-labels.
    """
    print("\n--- Bắt đầu huấn luyện Random Forest Risk Model ---")
    
    # Gom dữ liệu từ các file processed
    files = [f for f in os.listdir(data_dir) if f.startswith('processed_')]
    
    if not files:
        print("Không tìm thấy file processed data nào.")
        return None
        
    df_list = []
    for file in files:
        df_temp = pd.read_csv(os.path.join(data_dir, file))
        # Ánh xạ elevation dựa trên loại cây / file
        # Hardcode tạm cho nhanh vì ta biết nguồn gốc file
        if 'durian' in file:
            df_temp['elevation'] = LOCATION_MAPPING["Phường B'Lao"]['elevation']
        elif 'oolong' in file:
            df_temp['elevation'] = LOCATION_MAPPING["Phường Xuân Trường"]['elevation']
        else:
            df_temp['elevation'] = 1000 # default
            
        df_list.append(df_temp)
        
    df_full = pd.concat(df_list, ignore_index=True)
    
    # Đặc trưng đầu vào
    features = ['temp_max', 'temp_min', 'precipitation', 'elevation']
    target = 'risk_label'
    
    df_clean = df_full.dropna(subset=features + [target]).copy()
    
    X = df_clean[features]
    y = df_clean[target]
    
    # Mất cân bằng lớp - tính class weights hoặc oversample.
    # RF có class_weight='balanced'
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        class_weight='balanced',
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Lưu mô hình
    model_path = os.path.join(model_dir, 'risk_rf.pkl')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, model_path)
    print(f"Đã lưu mô hình rủi ro tại: {model_path}")
    
    return model

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    model_dir = os.path.join(base_dir, "ai_models")
    
    train_risk_model(model_dir, data_dir)
