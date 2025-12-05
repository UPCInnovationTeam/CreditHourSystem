import smtplib
from email.mime.text import MIMEText
import random
from app.core.config import sender_email
from app.core.config import sender_email_pwd as password
from typing import Dict, Tuple
import time
import threading
from passlib.context import CryptContext
import hashlib

records: dict[str, Tuple[str, float]] = {}

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# 注册时 - 密码哈希与存储
def hash_password(password_: str) -> str:
    return pwd_context.hash(password_)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def clean_expired_records(expiration_time: int = 300):
    """
    清理过期的验证码记录
    :param expiration_time: 过期时间（秒），默认300秒（5分钟）
    """
    current_time = time.time()
    expired_emails = [
        email for email, (_, timestamp) in records.items()
        if current_time - timestamp > expiration_time
    ]

    for email in expired_emails:
        del records[email]

    # print(f"清理了 {len(expired_emails)} 条过期记录")

    # 设置下一个定时清理任务
    timer = threading.Timer(60, clean_expired_records, kwargs={'expiration_time': expiration_time})
    timer.daemon = True
    timer.start()

def verify_code(email_target: str, verify_code_: str) -> bool:
    """
    验证验证码和邮箱是否匹配
    :param email_target: 被验证的目标邮箱
    :param verify_code_: 被验证的验证码
    :return: 验证是否通过
    """
    return verify_code_ == records.get(email_target or ("", 0))[0]

async def send_verify_code(email_target: str) -> str | None:
    """
    这是一个发送验证码的函数，通过邮箱发送
    :param email_target: 接受验证码的邮箱
    :return: 验证码的值
    """
    # 生成验证码
    verify_code = ''.join([str(random.randint(0,9)) for _ in range(6)])
    #设置SMTP服务器信息（163邮箱服务器）
    smtp_server = 'smtp.163.com'
    port = 465
    receiver_email = email_target

    #邮件内容
    message = MIMEText(f'您的验证码是{verify_code}')
    message['Subject'] = '验证码'
    message['From'] = sender_email
    message['To'] = receiver_email

    #发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_server, port)
        # server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        records[email_target] = (verify_code, time.time())
        return verify_code
    except Exception as e:
        print(f"发送邮件失败：{e}")
        return None

if __name__ == '__main__':
    print(send_verify_code("sudaowan@163.com"))


