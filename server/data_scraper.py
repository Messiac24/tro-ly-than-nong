import os
import random
import pandas as pd
import requests
from datetime import datetime, timedelta

# Khởi tạo thư mục data
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Thông số vùng canh tác
LOCATIONS = {
    "Phường B'Lao": {"lat": 11.5247, "lon": 107.859},
    "Phường Xuân Trường": {"lat": 11.89, "lon": 108.54}
}

def fetch_weather_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Gọi API Open-Meteo để lấy dữ liệu thời tiết quá khứ."""
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "Asia/Bangkok"
    }
    
    print(f"Fetching weather data for {lat}, {lon} from {start_date} to {end_date}...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    daily = data.get("daily", {})
    df = pd.DataFrame({
        "date": pd.to_datetime(daily.get("time")),
        "temp_max": daily.get("temperature_2m_max"),
        "temp_min": daily.get("temperature_2m_min"),
        "precipitation": daily.get("precipitation_sum")
    })
    
    return df

def generate_durian_prices(dates) -> list:
    """Sinh dữ liệu giá Sầu riêng Ri6 (Giảm vào tháng 6-8, cao vào nghịch vụ)."""
    prices = []
    for d in dates:
        month = d.month
        # Giá nền: 60k - 80k
        if month in [6, 7, 8]:
            base_price = random.uniform(50000, 65000)
        else:
            base_price = random.uniform(75000, 95000)
        
        # Thêm nhiễu
        price = base_price + random.uniform(-5000, 5000)
        prices.append(round(price, -3)) # làm tròn đến nghìn
    return prices

def generate_oolong_prices(dates, weather_df=None) -> list:
    """Sinh dữ liệu giá Chè Ô Long."""
    prices = []
    for i, d in enumerate(dates):
        base_price = 250000
        if weather_df is not None and i < len(weather_df):
            rain = weather_df.iloc[i]['precipitation']
            temp_min = weather_df.iloc[i]['temp_min']
            
            # Xử lý NaN
            if pd.isna(rain): rain = 0
            if pd.isna(temp_min): temp_min = 20
            
            if rain > 20: # Mưa nhiều
                base_price -= random.uniform(10000, 20000)
            elif temp_min < 10: # Lạnh sâu
                base_price += random.uniform(20000, 40000)
                
        price = base_price + random.uniform(-10000, 15000)
        prices.append(round(price, -3))
    return prices

def generate_coffee_prices(dates, base_price=70000) -> list:
    """Sinh dữ liệu giá Cà phê (Biến động theo chu kỳ và ngẫu nhiên)."""
    prices = []
    for i, d in enumerate(dates):
        # Giả lập xu hướng tăng nhẹ theo thời gian
        trend = i * 20 
        # Biến động mùa vụ (tháng 11-1 là mùa thu hoạch cà phê ở Tây Nguyên -> giá thường biến động)
        seasonal_effect = 5000 if d.month in [11, 12, 1] else 0
        
        price = base_price + trend + seasonal_effect + random.uniform(-3000, 3000)
        prices.append(round(price, -2))
    return prices

def main():
    print("Bắt đầu lấy dữ liệu và sinh dữ liệu giả lập...")
    
    # 2 năm dữ liệu
    end_date = datetime.now() - timedelta(days=5) # lùi lại 5 ngày để đảm bảo data có sẵn (archive-api trễ vài ngày)
    start_date = end_date - timedelta(days=2*365)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # 1. Sầu riêng Ri6 (B'Lao)
    print("Xử lý Sầu riêng Ri6 (B'Lao)...")
    df_weather_blao = fetch_weather_data(
        LOCATIONS["Phường B'Lao"]['lat'], 
        LOCATIONS["Phường B'Lao"]['lon'], 
        start_str, end_str
    )
    
    df_durian = df_weather_blao.copy()
    df_durian['crop'] = 'Sầu riêng Ri6'
    df_durian['price_vnd'] = generate_durian_prices(df_durian['date'])
    df_durian['source'] = 'AI_Synthetic'
    df_durian['is_synthetic'] = True
    
    path_durian = os.path.join(DATA_DIR, 'raw_durian_ri6.csv')
    df_durian.to_csv(path_durian, index=False)
    print(f"Đã lưu: {path_durian} ({len(df_durian)} dòng)")
    
    # 2. Chè Ô Long (Xuân Trường)
    print("Xử lý Chè Ô Long (Xuân Trường)...")
    df_weather_xuantruong = fetch_weather_data(
        LOCATIONS["Phường Xuân Trường"]['lat'], 
        LOCATIONS["Phường Xuân Trường"]['lon'], 
        start_str, end_str
    )
    
    df_oolong = df_weather_xuantruong.copy()
    df_oolong['crop'] = 'Chè Ô Long'
    df_oolong['price_vnd'] = generate_oolong_prices(df_oolong['date'], df_weather_xuantruong)
    df_oolong['source'] = 'AI_Synthetic'
    df_oolong['is_synthetic'] = True
    
    path_oolong = os.path.join(DATA_DIR, 'raw_oolong.csv')
    df_oolong.to_csv(path_oolong, index=False)
    print(f"Đã lưu: {path_oolong} ({len(df_oolong)} dòng)")

    # 3. Cà phê Robusta (B'Lao)
    print("Xử lý Cà phê Robusta (B'Lao)...")
    df_robusta = df_weather_blao.copy()
    df_robusta['crop'] = 'Cà phê Robusta'
    df_robusta['price_vnd'] = generate_coffee_prices(df_robusta['date'], base_price=120000)
    df_robusta['source'] = 'AI_Synthetic'
    df_robusta['is_synthetic'] = True
    path_robusta = os.path.join(DATA_DIR, 'raw_robusta.csv')
    df_robusta.to_csv(path_robusta, index=False)
    print(f"Đã lưu: {path_robusta}")

    # 4. Cà phê Arabica (Xuân Trường)
    print("Xử lý Cà phê Arabica (Xuân Trường)...")
    df_arabica = df_weather_xuantruong.copy()
    df_arabica['crop'] = 'Cà phê Arabica'
    df_arabica['price_vnd'] = generate_coffee_prices(df_arabica['date'], base_price=150000)
    df_arabica['source'] = 'AI_Synthetic'
    df_arabica['is_synthetic'] = True
    path_arabica = os.path.join(DATA_DIR, 'raw_arabica.csv')
    df_arabica.to_csv(path_arabica, index=False)
    print(f"Đã lưu: {path_arabica}")
    
    print("Hoàn tất Bước lấy dữ liệu!")

if __name__ == '__main__':
    main()
