
import os
import sys
import bcrypt
import datetime
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Thêm path để import models và database
sys.path.append(os.path.join(os.getcwd(), 'server'))
from database import SessionLocal, engine
import models

def seed_data():
    db = SessionLocal()
    
    # 1. Danh sách người dùng ảo
    fake_users = [
        ("Bác Năm Ri6", "bacnam@gmail.com"),
        ("Cô Lan Bảo Lộc", "colan@yahoo.com"),
        ("Anh Ba Cà Phê", "anhba@outlook.com"),
        ("Chú Sáu Sầu Riêng", "chusau@thannong.vn"),
        ("Hoàng Lộc", "hoangloc@nongsan.vn"),
        ("Nông dân Tèo", "teo@gmail.com"),
        ("Chị Hoa Lâm Đồng", "chihoa@gmail.com"),
        ("Chú Bảy Phân Bón", "chubay@gmail.com"),
        ("Út Hiền", "uthien@gmail.com"),
        ("Thanh Xuân Farm", "thanhxuan@farm.vn")
    ]
    
    # Hash mật khẩu "123"
    password = "123"
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    user_objects = []
    print("--- Đang tạo 10 người dùng ảo ---")
    for name, email in fake_users:
        # Kiểm tra nếu user đã tồn tại
        existing = db.query(models.User).filter(models.User.email == email).first()
        if not existing:
            user = models.User(
                email=email,
                hashed_password=hashed_pw,
                full_name=name,
                role="farmer"
            )
            db.add(user)
            db.flush() # Để lấy ID
            user_objects.append(user)
            print(f"✅ Đã tạo: {name} ({email})")
        else:
            user_objects.append(existing)

    # 2. Danh sách câu hỏi giả lập
    questions = [
        "Kỹ thuật bón phân cho sầu riêng Ri6 thế nào?",
        "Giá cà phê hôm nay tại Lâm Đồng bao nhiêu?",
        "Làm sao để phòng trừ sâu đục thân sầu riêng?",
        "Chi phí đầu tư 1ha cà phê là bao nhiêu?",
        "Sầu riêng bị rụng sinh lý thì phải làm sao?",
        "Kỹ thuật tưới nhỏ giọt cho cà phê?",
        "Bón phân gì để quả sầu riêng to và đẹp?",
        "Giá phân bón NPK hiện nay có tăng không?",
        "Lâm Đồng mùa này trồng cây gì hiệu quả?",
        "Kỹ thuật thu hoạch và bảo quản cà phê nhân?",
        "Sâu bệnh hại lá sầu riêng xử lý thế nào?",
        "Hỏi về giống sầu riêng Musang King?",
        "Giá sầu riêng tại vườn hôm nay?",
        "Cách ủ phân hữu cơ từ vỏ cà phê?"
    ]
    
    answers = [
        "Dạ, bà con lưu ý bón phân theo 4 giai đoạn: sau thu hoạch, trước nở hoa, nuôi quả và chín...",
        "Hiện tại giá cà phê đang dao động từ 120,000 - 125,000đ/kg tùy khu vực Bảo Lộc, Di Linh...",
        "Bà con cần dọn vườn sạch sẽ, dùng thuốc đặc trị và kiểm tra thân cây thường xuyên...",
        "Chi phí đầu tư khoảng 150-200 triệu đồng cho năm đầu tiên bao gồm giống, phân bón...",
        "Rụng sinh lý là bình thường, nhưng cần bổ sung Canxi Bo để giảm thiểu...",
        "Hệ thống tưới nhỏ giọt giúp tiết kiệm 30% lượng nước và phân bón bón trực tiếp qua vòi...",
        "Nên dùng phân bón giàu Kali ở giai đoạn cuối để tăng chất lượng trái..."
    ]

    print("\n--- Đang tạo 30 cuộc hội thoại giả lập ---")
    for _ in range(30):
        user = random.choice(user_objects)
        q = random.choice(questions)
        a = random.choice(answers)
        
        # Tạo thời gian ngẫu nhiên trong 7 ngày qua
        days_ago = random.randint(0, 7)
        created_at = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago)
        
        chat = models.ChatHistory(
            user_id=user.id,
            question=q,
            answer=a,
            created_at=created_at
        )
        db.add(chat)

    db.commit()
    print("\n🚀 HOÀN TẤT: Dashboard của bạn hiện đã đầy đủ dữ liệu người dùng và xu hướng!")

if __name__ == "__main__":
    seed_data()
