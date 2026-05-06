import os
import sys
from datetime import datetime

# Thêm thư mục server vào sys.path
sys.path.append(os.path.join(os.getcwd(), "server"))

from ml.inference import predict_price

def test():
    print("--- Test Dự báo giá bằng TFT ---")
    try:
        # Test Robusta
        print("\nĐang dự báo cho Cà phê Robusta...")
        forecast = predict_price("Cà phê Robusta", 125000, "Phường B'Lao")
        print(f"Dự báo 30 ngày thành công. 5 ngày đầu tiên:")
        for f in forecast[:5]:
            print(f"Ngày: {f['date']} | Giá: {f['predicted']:.0f} (Min: {f['min']:.0f}, Max: {f['max']:.0f})")
            
        # Test Arabica
        print("\nĐang dự báo cho Cà phê Arabica...")
        forecast_ara = predict_price("Cà phê Arabica", 155000, "Phường Xuân Trường")
        print(f"Dự báo 30 ngày thành công. Ngày cuối cùng:")
        print(f"Ngày: {forecast_ara[-1]['date']} | Giá: {forecast_ara[-1]['predicted']:.0f}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
