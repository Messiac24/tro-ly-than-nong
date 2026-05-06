import sys
import os
from pathlib import Path
import random
import datetime

# Setup path
BASE_DIR = Path(__file__).resolve().parent
SERVER_DIR = BASE_DIR / "server"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

try:
    from database import SessionLocal, engine
    import models
except ImportError:
    from server.database import SessionLocal, engine
    from server import models
import bcrypt

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

db = SessionLocal()

# 1. Danh sách người dùng mẫu
test_users = [
    {"username": "cobay", "name": "Cô Bảy Nông Dân", "email": "cobay@gmail.com"},
    {"username": "bactu", "name": "Bác Tư Làm Vườn", "email": "bactu@gmail.com"},
    {"username": "anhnam", "name": "Anh Năm Cà Phê", "email": "anhnam@gmail.com"},
    {"username": "chihai", "name": "Chị Hai Trà Oolong", "email": "chihai@gmail.com"},
    {"username": "chusau", "name": "Chú Sáu Sầu Riêng", "email": "chusau@gmail.com"},
    {"username": "dimuoi", "name": "Dì Mười Bảo Lộc", "email": "dimuoi@gmail.com"},
    {"username": "cauut", "name": "Cậu Út Đà Lạt", "email": "cauut@gmail.com"},
    {"username": "diut", "name": "Dì Út Xuân Trường", "email": "diut@gmail.com"},
    {"username": "ongtam", "name": "Ông Tám Trạm Hành", "email": "ongtam@gmail.com"},
    {"username": "baba", "name": "Bà Ba Canh Tác", "email": "baba@gmail.com"},
]

print("--- Dang tao nguoi dung mau ---")
user_objects = []
for u in test_users:
    existing = db.query(models.User).filter(models.User.username == u["username"]).first()
    if not existing:
        new_user = models.User(
            username=u["username"],
            email=u["email"],
            full_name=u["name"],
            hashed_password=get_password_hash("123"),
            role="farmer"
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user_objects.append(new_user)
        print(f"Da tao: {u['username']}")
    else:
        user_objects.append(existing)

# 2. Tao du lieu tra cuu mau (de ve bieu do)
locations = ["Phường B'Lao", "Phường Xuân Trường"]
crops = ["Sầu riêng Ri6", "Cà phê Robusta (TR4/TR9)", "Chè Oolong"]
modes = ["Kinh doanh (Thu hoạch)", "Kiến thiết cơ bản (Trồng mới)"]

print("\n--- Dang tao lich su tra cuu mau ---")
for user in user_objects:
    # Moi user tra cuu tu 2-4 lan
    for _ in range(random.randint(2, 4)):
        history = models.SearchHistory(
            user_id=user.id,
            location=random.choice(locations),
            crop=random.choice(crops),
            mode=random.choice(modes),
            capital=random.uniform(50, 500),
            area_ha=random.uniform(0.5, 5.0),
            risk_level=random.choice(["Thấp", "Trung bình", "Cao"]),
            recommendation="Dữ liệu mẫu cho báo cáo đồ án.",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))
        )
        db.add(history)

# 3. Tao du lieu Chat mau
questions = [
    "Kỹ thuật bón phân sầu riêng Ri6?",
    "Giá cà phê hôm nay bao nhiêu?",
    "Chi phí trồng 1ha chè Oolong?",
    "Làm sao để trị bệnh rỉ sắt trên cà phê?",
    "Nên thu hoạch sầu riêng vào tháng mấy?"
]

print("\n--- Dang tao lich su chat mau ---")
for user in user_objects:
    for _ in range(random.randint(1, 3)):
        chat = models.ChatHistory(
            user_id=user.id,
            question=random.choice(questions),
            answer="Đây là câu trả lời mẫu từ trợ lý AI Thần Nông.",
            created_at=datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(0, 30))
        )
        db.add(chat)

db.commit()
db.close()
print("\n=== DA NAP DU LIEU MAU THANH CONG! ===")
