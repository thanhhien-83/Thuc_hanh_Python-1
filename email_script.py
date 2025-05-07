import smtplib
import imaplib
import email
from email.mime.text import MIMEText

# === BƯỚC 1: Đọc thông tin tài khoản ===
try:
    with open('email_credentials.txt', 'r') as file:
        account_info = file.readlines()
        email_address = account_info[0].strip()
        app_password = account_info[1].strip()
except FileNotFoundError:
    print("❌ Lỗi: Không tìm thấy file email_credentials.txt")
    exit()

# === BƯỚC 2: Đọc nội dung email, người nhận, và tiêu chí lọc ===
try:
    with open('email_content.txt', 'r', encoding='utf-8') as file:
        email_content = file.read()
except FileNotFoundError:
    print("❌ Lỗi: Không tìm thấy file email_content.txt")
    exit()

try:
    with open('recipient.txt', 'r') as file:
        recipient_email = file.read().strip()
except FileNotFoundError:
    print("❌ Lỗi: Không tìm thấy file recipient.txt")
    exit()

try:
    with open('email_filter.txt', 'r') as file:
        filter_sender = file.read().strip()
except FileNotFoundError:
    print("❌ Lỗi: Không tìm thấy file email_filter.txt")
    exit()

# === BƯỚC 3: Gửi email ===
msg = MIMEText(email_content, _charset="utf-8")
msg['Subject'] = 'Email Tự Động từ VSCode'
msg['From'] = email_address
msg['To'] = recipient_email

try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_address, app_password)
        server.send_message(msg)
    print("✅ Email đã được gửi thành công!")
except Exception as e:
    print(f"❌ Lỗi khi gửi email: {e}")
    exit()

# === BƯỚC 4: Nhận email từ người gửi cụ thể ===
try:
    with imaplib.IMAP4_SSL('imap.gmail.com') as server:
        server.login(email_address, app_password)
        server.select('INBOX')

        # Tìm các email từ người gửi
        _, data = server.search(None, f'FROM "{filter_sender}"')

        if data[0] == b'':
            print(f"⚠️ Không tìm thấy email nào từ {filter_sender}")
        else:
            for num in data[0].split():
                _, msg_data = server.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                email_msg = email.message_from_bytes(raw_email)

                subject = email_msg['subject'] or '(Không có tiêu đề)'
                print(f"\n📩 Tiêu đề email: {subject}")

                # Xử lý nội dung
                body = ""
                if email_msg.is_multipart():
                    for part in email_msg.walk():
                        if part.get_content_type() == 'text/plain':
                            charset = part.get_content_charset() or 'utf-8'
                            body = part.get_payload(decode=True).decode(charset, errors='replace')
                            break
                else:
                    charset = email_msg.get_content_charset() or 'utf-8'
                    body = email_msg.get_payload(decode=True).decode(charset, errors='replace')

                print("📨 Nội dung email:")
                print(body)
                break  # Chỉ đọc email đầu tiên
except Exception as e:
    print(f"❌ Lỗi khi nhận email: {e}")