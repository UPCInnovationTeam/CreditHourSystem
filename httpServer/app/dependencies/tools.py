import smtplib
from email.mime.text import MIMEText
import random

def send_verify_code(email_target: str) -> str:
    """
    这是一个发送验证码的函数，通过邮箱发送
    :param email_target: 接受验证码的邮箱
    :return: 验证码的值
    """
    # 生成验证码
    verify_code = ''.join([str(random.randint(0,9)) for _ in range(6)])
    #设置SMTP服务器信息（163邮箱服务器）
    smtp_server = 'smtp.163.com'
    port = 25
    sender_email = "19862266073@163.com"
    receiver_email = email_target
    password = "KNxM5LZHRWjZyXYW"

    #邮件内容
    message = MIMEText(f'您的验证码是{verify_code}')
    message['Subject'] = '验证码'
    message['From'] = sender_email
    message['To'] = receiver_email

    #发送邮件
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        return verify_code
    except Exception as e:
        print(f"发送邮件失败：{e}")
        return None

if __name__ == '__main__':
    print(send_verify_code("sudaowan@163.com"))


