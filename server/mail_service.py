import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Gmail SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
def send_otp_email(to_email: str, otp_code: str):
    """Gửi mã OTP qua Gmail SMTP"""
    # Đọc lại .env để lấy giá trị mới nhất
    load_dotenv(override=True)
    sender_email = os.getenv("EMAIL_HOST_USER")
    sender_password = os.getenv("EMAIL_HOST_PASSWORD")

    if not sender_email or not sender_password:
        print(f"❌ Lỗi: Chưa cấu hình EMAIL_HOST_USER hoặc EMAIL_HOST_PASSWORD trong .env (Email: {sender_email})")
        return False

    try:
        msg = MIMEMultipart()
        # Hiển thị tên người gửi chuyên nghiệp
        msg['From'] = f"Trợ Lý Thần Nông <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = f"{otp_code} là mã xác nhận Trợ Lý Thần Nông của bạn"

        html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; background-color: #f9f9f9;">
            <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2e7d32; margin: 0; font-size: 28px;">Trợ Lý Thần Nông 🌾</h1>
                    <p style="color: #666; margin-top: 8px;">Hệ thống tư vấn nông nghiệp thông minh</p>
                </div>
                
                <div style="border-top: 1px solid #eee; padding-top: 30px;">
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">Chào bạn,</p>
                    <p style="font-size: 16px; color: #333; line-height: 1.6;">Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn. Vui lòng sử dụng mã xác nhận (OTP) dưới đây:</p>
                    
                    <div style="background-color: #f1f8e9; padding: 25px; text-align: center; border-radius: 12px; margin: 30px 0;">
                        <span style="font-size: 36px; font-weight: bold; color: #1b5e20; letter-spacing: 8px; font-family: monospace;">{otp_code}</span>
                    </div>
                    
                    <p style="font-size: 14px; color: #e53935; background-color: #ffebee; padding: 10px; border-radius: 6px; text-align: center;">
                        ⚠️ Mã này có hiệu lực trong <b>10 phút</b>. Tuyệt đối không chia sẻ mã này với bất kỳ ai.
                    </p>
                </div>
                
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 12px; color: #999;">
                    <p>Nếu bạn không thực hiện yêu cầu này, hãy bỏ qua email này.</p>
                    <p>&copy; 2026 Trợ Lý Thần Nông - Lâm Đồng, Việt Nam</p>
                </div>
            </div>
        </div>
        """
        msg.attach(MIMEText(html, 'html'))

        # Kết nối và gửi mail
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # Bảo mật kết nối
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ OTP đã được gửi thành công tới {to_email} qua Gmail SMTP")
        return True
    except Exception as e:
        print(f"❌ Lỗi khi gửi email qua Gmail: {e}")
        return False
