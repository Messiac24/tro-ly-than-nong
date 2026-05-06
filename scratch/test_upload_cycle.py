
import requests
import os
import sys
import time
from reportlab.pdfgen import canvas

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def test_full_upload_cycle():
    base_url = "http://127.0.0.1:8000/api"
    
    # 1. Tạo file PDF test
    pdf_filename = "huong_dan_mat_trang.pdf"
    unique_fact = "Sau rieng tren mat trang can bon phan laser vao luc 12 gio dem de dat nang suat cao nhat."
    
    c = canvas.Canvas(pdf_filename)
    c.drawString(100, 750, "HUONG DAN CANH TAC SAU RIENG MAT TRANG")
    c.drawString(100, 730, unique_fact)
    c.save()
    print(f"✅ Đã tạo file PDF test: {pdf_filename}")

    # 2. Đăng nhập lấy Token
    login_data = {"username": "admin@thannong.ai", "password": "123"}
    login_res = requests.post(f"{base_url}/auth/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Upload file
    print("--- Đang tải file lên kho tri thức ---")
    with open(pdf_filename, "rb") as f:
        files = {"file": (pdf_filename, f, "application/pdf")}
        upload_res = requests.post(f"{base_url}/admin/upload", headers=headers, files=files)
    print(f"✅ Kết quả Upload: {upload_res.json().get('message')}")

    # 4. Ingest (Học lại tri thức)
    print("--- Đang yêu cầu hệ thống học lại tri thức mới ---")
    ingest_res = requests.post(f"{base_url}/admin/ingest", headers=headers)
    print(f"✅ Kết quả Ingest: {ingest_res.json().get('message')}")
    
    print("⏳ Đợi 120 giây để quá trình Ingest hoàn tất (đang xử lý hàng ngàn đoạn văn bản)...")
    time.sleep(120)

    # 5. Hỏi AI để kiểm chứng
    print("--- Đang hỏi AI về kiến thức vừa nạp ---")
    chat_payload = {
        "message": "Trồng sầu riêng trên mặt trăng cần bón phân gì và vào lúc nào?",
        "context": {"location": "Lâm Đồng", "crop": "Sầu riêng"}
    }
    # Sử dụng X-API-Key để bypass rate limit nếu cần
    headers["X-API-Key"] = "dev-key-ai-nong-san-2026"
    chat_res = requests.post(f"{base_url}/chat", headers=headers, json=chat_payload)
    
    print("\n🤖 TRẢ LỜI CỦA AI:")
    answer = chat_res.json().get("answer", "")
    print(answer)

    if "laser" in answer.lower() or "12 giờ đêm" in answer.lower():
        print("\n✨ KẾT QUẢ: THÀNH CÔNG! AI đã học được kiến thức từ file vừa upload.")
    else:
        print("\n❌ KẾT QUẢ: THẤT BẠI. AI chưa cập nhật được tri thức mới.")

    # Dọn dẹp
    if os.path.exists(pdf_filename):
        os.remove(pdf_filename)

if __name__ == "__main__":
    test_full_upload_cycle()
