
import requests
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_admin_features():
    base_url = "http://127.0.0.1:8000/api/admin"
    
    # 1. Đăng nhập lấy Token
    login_url = "http://127.0.0.1:8000/api/auth/login"
    login_data = {"username": "admin@thannong.ai", "password": "123"}
    login_res = requests.post(login_url, data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("--- 1. Kiểm tra danh sách File tri thức ---")
    files_res = requests.get(f"{base_url}/files", headers=headers)
    if files_res.status_code == 200:
        files = files_res.json()
        print(f"✅ Tìm thấy {len(files)} file PDF trong kho.")
        for f in files[:3]:
            print(f"   - {f['name']} ({round(f['size']/1024, 1)} KB)")
    else:
        print(f"❌ Lỗi lấy danh sách file: {files_res.status_code}")

    print("\n--- 2. Kiểm tra phân tích Xu hướng (Trends) ---")
    trends_res = requests.get(f"{base_url}/trends", headers=headers)
    if trends_res.status_code == 200:
        trends = trends_res.json()
        if len(trends) > 0:
            print(f"✅ Đã phân tích được {len(trends)} chủ đề hot.")
            for t in trends:
                print(f"   🔥 {t['topic']}: {t['count']} lượt quan tâm")
        else:
            print("ℹ️ Chưa có đủ dữ liệu chat để phân tích xu hướng.")
    else:
        print(f"❌ Lỗi lấy xu hướng: {trends_res.status_code}")

if __name__ == "__main__":
    test_admin_features()
